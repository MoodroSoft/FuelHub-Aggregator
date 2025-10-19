import os
import sys
import nest_asyncio
from typing import AsyncGenerator

import pytest
from alembic.config import main as alembic_run
from sqlalchemy import AsyncAdaptedQueuePool, text
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.ext.asyncio.session import async_sessionmaker
from redis.asyncio import Redis, ConnectionPool
import httpx

nest_asyncio.apply()

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'src/'))

from core.redis_client import get_redis
from main import app
from core.config import settings
from core.models import Base
from core.database import database

from tests.fixtures.data import *


pytestmark = pytest.mark.anyio


@pytest.hookimpl(trylast=True)
def pytest_runtest_setup(item) -> None:
    if "session" in item.funcargs.keys():
        item.funcargs["session"].expunge_all()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def monkey_fixture():
    """Returns MonkeyPatch object to allow monkeypatch to work in session scope"""
    from _pytest.monkeypatch import MonkeyPatch

    mpatch: MonkeyPatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session")
def override_database_settings(monkey_fixture) -> None:
    """In case we run tests using default docker-compose,
    overrides database env-variables to handle connection to test database"""

    worker_id: str | None = os.environ.get("PYTEST_XDIST_WORKER")

    if worker_id:
        if settings.POSTGRES_DB.endswith(f"_test{worker_id}"):
            monkey_fixture.setattr(
                settings, "POSTGRES_DB", f"{settings.POSTGRES_DB}{worker_id}"
            )
        else:
            monkey_fixture.setattr(
                settings, "POSTGRES_DB", f"{settings.POSTGRES_DB}_test{worker_id}"
            )
    else:
        if settings.POSTGRES_DB.endswith("_test"):
            monkey_fixture.setattr(settings, "POSTGRES_DB", settings.POSTGRES_DB)
        else:
            monkey_fixture.setattr(
                settings, "POSTGRES_DB", f"{settings.POSTGRES_DB}_test"
            )

    # Overrides pgbouncer env-variables to bypass pgbouncer connection and connect to postgres instance straightaway
    monkey_fixture.setattr(settings, "PG_BOUNCER_HOST", settings.POSTGRES_HOST)
    monkey_fixture.setattr(settings, "PG_BOUNCER_PORT", 5432)


@pytest.fixture(scope="session", autouse=True)
async def setup_db(override_database_settings):
    """
    BASE DB SETUP - recreate DB, run all migrations
    """

    if os.getenv("IS_TEST_ENVIRONMENT"):
        database_url: str = (
            f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
            f"{settings.PG_BOUNCER_HOST}:{settings.PG_BOUNCER_PORT}/{settings.POSTGRES_DB}"
        )

        engine: AsyncEngine = create_async_engine(
            database_url,
            echo=settings.DB_ECHO,
            future=True,
            poolclass=AsyncAdaptedQueuePool,
        )
        # удаление таблиц для очистки базы данных
        async with engine.begin() as conn:
            await conn.execute(text("DROP SCHEMA if exists public CASCADE;"))
            await conn.execute(text("CREATE SCHEMA public;"))
        await engine.dispose()

    else:
        # подключение к текущей бд и создание тестовой
        database_url = (
            f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
            f"@{settings.POSTGRES_HOST}/postgres"
        )

        engine = create_async_engine(
            database_url,
            echo=settings.DB_ECHO,
            future=True,
            isolation_level="AUTOCOMMIT",
            poolclass=AsyncAdaptedQueuePool,
        )
        async with engine.begin() as conn:
            await conn.execute(text(f"DROP DATABASE IF EXISTS {settings.POSTGRES_DB}"))
            await conn.execute(text(f"CREATE DATABASE {settings.POSTGRES_DB}"))
        await engine.dispose()

        # Настройка подключения к изолированной тестовой базе данных (в рамках сессии)
        database_url = (
            f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
            f"@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"
        )

        engine = create_async_engine(
            database_url,
            echo=settings.DB_ECHO,
            future=True,
            poolclass=AsyncAdaptedQueuePool,
        )

    print(
        "\n\n# ------------------------------ RUNNING ALEMBIC MIGRATIONS ------------------------------ #\n"
    )  # noqa

    # запуск миграций
    alembic_run(
        [
            "-c",
            "../src/alembic.ini",
            "-n",
            "alembic_test",
            "--raiseerr",
            "upgrade",
            "head",
        ]
    )

    print(
        "\n# ------------------------------ FINISHED RUNNING ALEMBIC MIGRATIONS ------------------------------ #\n"
    )

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture(scope="function", name="redis", autouse=True)
async def setup_redis(monkeypatch) -> AsyncGenerator[Redis, None]:
    """Получение и очистка redis после каждого теста."""

    if not os.environ.get("PYTEST_XDIST_WORKER"):
        redis_connection_url = (
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        )
    else:
        redis_connection_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{int(os.environ.get('PYTEST_XDIST_WORKER').split('gw')[1])}"

    redis_pool = ConnectionPool.from_url(
        url=redis_connection_url,
        decode_responses=True,
        max_connections=100,
    )

    monkeypatch.setattr("core.redis_client.redis_pool", redis_pool)

    # вызов общего get_redis приведет к тому что значение вернется в обход патча значения core.redis_client.redis_connection_url
    redis = Redis(connection_pool=redis_pool)
    await redis.flushdb(asynchronous=True)
    yield redis
    await redis.flushdb(asynchronous=True)


@pytest.fixture(scope="session")
async def db_engine(override_database_settings) -> AsyncGenerator:
    """
    Creates engine for all tests
    """

    database_url: str = (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.PG_BOUNCER_HOST}:{settings.PG_BOUNCER_PORT}/{settings.POSTGRES_DB}"
    )
    engine: AsyncEngine = create_async_engine(
        database_url, echo=settings.DB_ECHO, future=True
    )

    yield engine

    await engine.dispose()


@pytest.fixture(scope="function", name="session")
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator:
    """
    Creating a session, separate for each function

    scope=session - должна запускаться один раз на прогон вех тестов!
    """

    async_session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture(scope="function", name="mock_async_session", autouse=True)
async def mock_async_session(db_engine: AsyncEngine, monkeypatch):
    """
    Подмена async_session с engine для тестов.
    """

    new_async_session = async_sessionmaker(db_engine, expire_on_commit=False)
    monkeypatch.setattr("core.database.database.session_factory", new_async_session)


@pytest.fixture(scope="function", autouse=True)
async def client(db_engine: AsyncEngine):

    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(db_engine, expire_on_commit=False)

    async def get_session_override() -> AsyncGenerator:
        async with async_session.begin() as session:
            yield session

    app.dependency_overrides[database.get_session] = get_session_override

    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)

    async with httpx.AsyncClient(
        transport=transport, base_url="https://agai.test/"
    ) as client:
        yield client

    app.dependency_overrides.clear()

    # Drop tables
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

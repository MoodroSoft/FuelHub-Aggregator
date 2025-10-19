from asyncio import current_task
from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    AsyncEngine,
    async_scoped_session,
    async_sessionmaker,
)
from core.config import settings


class Database:
    def __init__(self, url: str, echo: bool = False):
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            future=True,
            pool_pre_ping=True,
            max_overflow=60,
            pool_size=20,
            pool_timeout=30,
            pool_recycle=600,
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False
        )

    async def get_session(self) -> AsyncIterator[AsyncSession]:
        """
        Автоматический коммит сессии если не возникла ошибка, иначе откат транзакции
        """
        async with self.session_factory() as session:
            async with session.begin():
                yield session

    async def get_session_manual(self) -> AsyncIterator[AsyncSession]:
        """
        Необходимо вручную закрыть сессию (коммит или откат транзакции).
        Для случаев, когда нужно управлять транзакциями самостоятельно
        """
        async with self.session_factory() as session:
            yield session

    @asynccontextmanager
    async def scoped_session(self) -> AsyncIterator[AsyncSession]:
        """
        Для Celery-воркеров
        """
        scoped_factory = async_scoped_session(
            self.session_factory,
            scopefunc=current_task,
        )
        try:
            async with scoped_factory() as s:
                yield s
        finally:
            await scoped_factory.remove()


database = Database(settings.database_url, settings.DB_ECHO)

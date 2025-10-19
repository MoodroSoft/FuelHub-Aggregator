import asyncio
from logging.config import fileConfig

from sqlalchemy import Connection, engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context

from core.config import settings
from core.models.base import Base


DATABASE_URL = "postgresql+asyncpg://{0}:{1}@{2}/{3}".format(
    settings.POSTGRES_USER,
    settings.POSTGRES_PASSWORD,
    settings.POSTGRES_HOST,
    settings.POSTGRES_DB,
)
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


# https://github.com/kvesteri/sqlalchemy-utils/issues/400
def render_item(type_, obj, autogen_context):
    """Apply rendering for custom sqlalchemy types"""
    if type_ == "type":
        module_name = obj.__class__.__module__
        if module_name.startswith("sqlalchemy_utils."):
            return render_sqlalchemy_utils_type(obj, autogen_context)

    # render default
    return False


def render_sqlalchemy_utils_type(obj, autogen_context):
    class_name = obj.__class__.__name__
    import_statement = f"from sqlalchemy_utils.types import {class_name}"
    autogen_context.imports.add(import_statement)
    if class_name == "ChoiceType":
        return render_choice_type(obj, autogen_context)
    return f"{class_name}()"


def render_choice_type(obj, autogen_context):
    choices = obj.choices

    if obj.type_impl.__class__.__name__ == "EnumTypeImpl":
        choices = obj.type_impl.enum_class.__name__
        import_statement = f"from models import {choices}"
        autogen_context.imports.add(import_statement)
    elif obj.type_impl.__class__.__name__ == "ChoiceTypeImpl":
        choices = list(obj.type_impl.choices_dict.items())

    # check if length is present and not null
    if hasattr(obj.impl, "length") and obj.impl.length:
        impl_stmt = f"sa.{obj.impl.__class__.__name__}({obj.impl.length})"
    else:
        impl_stmt = f"sa.{obj.impl.__class__.__name__}()"
    return f"{obj.__class__.__name__}(choices={choices}, impl={impl_stmt})"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        # TODO NEEDS CHECK!
        compare_type=True,
        # not stable! - https://github.com/sqlalchemy/alembic/issues/272
        # produces SELECT '{}'::json = '{}' AS anon_1 which causes error when comparing JSON fields
        # compare_server_default=my_compare_server_default,
        target_metadata=target_metadata,
        render_item=render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = AsyncEngine(
        engine_from_config(
            {"sqlalchemy.url": DATABASE_URL},
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())

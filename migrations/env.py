import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool

from logging.config import fileConfig
import database
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from models import Base
from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", database.URL_DATABASE + "?async_fallback=True")

target_metadata = Base.metadata


# Перемещаем connectable выше!
connectable = create_async_engine(
    config.get_main_option("sqlalchemy.url"),
    poolclass=pool.NullPool,
)


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


# Запуск миграций
asyncio.run(run_migrations_online())

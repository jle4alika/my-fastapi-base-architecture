"""Async SQLAlchemy engine (PostgreSQL / asyncpg)."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool

from core.config import settings


def get_database_url() -> str:
    """URL БД для приложения и Alembic (postgresql+asyncpg)."""

    if settings.db.TEST_URL:
        return settings.db.TEST_URL
    return settings.db.url_asyncpg


def _build_engine(*, null_pool: bool = False) -> AsyncEngine:
    connect_args: dict = {}
    engine_kwargs: dict = {}

    if settings.db.USE_PGBOUNCER:
        # PgBouncer transaction mode: отключаем prepared statements в asyncpg
        connect_args["statement_cache_size"] = 0
        engine_kwargs["poolclass"] = NullPool
    elif null_pool:
        engine_kwargs["poolclass"] = NullPool

    if connect_args:
        engine_kwargs["connect_args"] = connect_args

    return create_async_engine(get_database_url(), **engine_kwargs)


engine = _build_engine()
null_pool_engine = _build_engine(null_pool=True)


async def create_db_and_tables() -> None:
    """Создаёт таблицы по metadata (dev; в проде — Alembic)."""

    from sqlalchemy import text

    from infrastructure.postgres.base import Base

    async with engine.begin() as conn:
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto"'))
        await conn.run_sync(Base.metadata.create_all)

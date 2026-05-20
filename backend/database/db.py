"""
Базовая настройка SQLAlchemy: движок, сессии, типы колонок.
"""

from __future__ import annotations

import asyncio
import datetime
import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy.pool import NullPool
from sqlalchemy.types import Uuid

from backend.project_config import settings


def get_database_url() -> str:
    """URL БД для приложения и Alembic (asyncpg / aiosqlite)."""

    if settings.TEST_DATABASE_URL:
        return settings.TEST_DATABASE_URL
    if settings.USE_SQLITE:
        return settings.DATABASE_URL_sqlite
    return settings.DATABASE_URL_asyncpg


_database_url = get_database_url()
_use_sqlite = "sqlite" in _database_url

_connect_args: dict = {}
if not _use_sqlite and settings.USE_PGBOUNCER:
    # PgBouncer transaction mode: отключаем prepared statements в asyncpg
    _connect_args["statement_cache_size"] = 0

_engine_kwargs: dict = {"connect_args": _connect_args}
if not _use_sqlite and settings.USE_PGBOUNCER:
    _engine_kwargs["poolclass"] = NullPool

engine = create_async_engine(_database_url, **_engine_kwargs)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: одна сессия на запрос."""

    async with async_session() as session:
        yield session


idpk = Annotated[
    uuid.UUID,
    mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4),
]

if _use_sqlite:
    created_time = Annotated[
        datetime.datetime,
        mapped_column(default=datetime.datetime.utcnow),
    ]
    updated_time = Annotated[
        datetime.datetime,
        mapped_column(
            default=datetime.datetime.utcnow,
            onupdate=datetime.datetime.utcnow,
        ),
    ]
else:
    created_time = Annotated[
        datetime.datetime,
        mapped_column(server_default=text("TIMEZONE('utc', now())")),
    ]
    updated_time = Annotated[
        datetime.datetime,
        mapped_column(
            server_default=text("TIMEZONE('utc', now())"),
            onupdate=datetime.datetime.utcnow,
        ),
    ]


class Base(DeclarativeBase):
    """Базовый класс ORM-моделей."""

    repr_cols: set = set()
    repr_cols_num: int = 3

    def __repr__(self) -> str:
        cols = []
        repr_cols = getattr(self.__class__, "repr_cols", set())
        repr_cols_num = getattr(self.__class__, "repr_cols_num", 3)
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in repr_cols or idx < repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")
        return f"<{self.__class__.__name__} {', '.join(cols)}>"


async def create_db_and_tables() -> None:
    """Создаёт таблицы по metadata (dev; в проде — Alembic)."""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(create_db_and_tables())

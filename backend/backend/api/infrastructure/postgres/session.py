"""Async session makers и FastAPI-зависимость get_session."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from infrastructure.postgres.engine import engine, null_pool_engine

session_maker = async_sessionmaker(engine, expire_on_commit=False)
null_pool_session_maker = async_sessionmaker(
    bind=null_pool_engine,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: одна сессия на запрос."""

    async with session_maker() as session:
        yield session

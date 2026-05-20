"""
Адаптер БД fastapi-users: связь SQLAlchemy-сессии и модели User.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.db import get_session
from backend.database.models.user import User


async def get_user_db(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    """Dependency: адаптер fastapi-users для текущей сессии."""

    yield SQLAlchemyUserDatabase(session, User)

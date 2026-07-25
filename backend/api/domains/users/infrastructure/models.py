"""
ORM-модель пользователя (persistence).

Anti-corruption: fastapi-users / SQLAlchemy живут здесь, не в domain/.
"""

from __future__ import annotations

import uuid

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.postgres.base import UUIDBase


class UserModel(SQLAlchemyBaseUserTable[uuid.UUID], UUIDBase):
    """Таблица users для SQLAlchemy + fastapi-users."""

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(unique=True, index=True)

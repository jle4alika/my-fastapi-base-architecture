"""
ORM-модель пользователя на базе fastapi-users (SQLAlchemy).
"""

from __future__ import annotations

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.db import Base, created_time, updated_time


class User(SQLAlchemyBaseUserTableUUID, Base):
    """
    Пользователь: поля fastapi-users + доменные поля шаблона.

    Базовый класс уже содержит: id, email, hashed_password,
    is_active, is_superuser, is_verified.
    """

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(unique=True, index=True)
    birthday: Mapped[str] = mapped_column(default="")
    description: Mapped[str | None] = mapped_column(nullable=True, default=None)

    created_time: Mapped[created_time]
    updated_time: Mapped[updated_time]

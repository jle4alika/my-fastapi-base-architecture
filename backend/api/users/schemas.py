"""
Pydantic-схемы fastapi-users: чтение, создание, обновление пользователя.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

import re

from fastapi_users import schemas
from pydantic import Field, field_validator

_USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]+$")


class UserRead(schemas.BaseUser[uuid.UUID]):
    """Пользователь в ответах API (после регистрации, /users/me и т.д.)."""

    username: str
    birthday: str = ""
    description: str | None = None
    created_time: datetime | None = None
    updated_time: datetime | None = None


class UserCreate(schemas.BaseUserCreate):
    """Регистрация: email, пароль и дополнительные поля шаблона."""

    username: str = Field(min_length=3, max_length=32)
    birthday: date | None = None
    description: str | None = Field(default=None, max_length=512)

    @field_validator("username")
    @classmethod
    def _validate_username(cls, value: str) -> str:
        if not _USERNAME_PATTERN.fullmatch(value):
            msg = "username: только латиница, цифры и '_'"
            raise ValueError(msg)
        return value


class UserUpdate(schemas.BaseUserUpdate):
    """Обновление профиля (PATCH /users/me через fastapi-users)."""

    username: str | None = Field(default=None, min_length=3, max_length=32)
    birthday: date | None = None
    description: str | None = Field(default=None, max_length=512)

    @field_validator("username")
    @classmethod
    def _validate_username(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not _USERNAME_PATTERN.fullmatch(value):
            msg = "username: только латиница, цифры и '_'"
            raise ValueError(msg)
        return value

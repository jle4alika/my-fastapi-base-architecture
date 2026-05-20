"""
Входные DTO для ручек, связанных с пользователем.

Регистрация и обновление профиля — через fastapi-users (api/users/schemas.py).
Здесь — вспомогательные схемы для кастомных ручек при необходимости.
"""

from __future__ import annotations

import re
from datetime import date

from pydantic import EmailStr, Field, field_validator, model_validator

from backend.api.schemas.dto.base import BaseDTO

_USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]+$")


class _UsernameMixin(BaseDTO):
    """Валидация username для DTO."""

    @field_validator("username", check_fields=False)
    @classmethod
    def _validate_username(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not _USERNAME_PATTERN.fullmatch(value):
            raise ValueError(
                "username может содержать только латинские буквы, цифры и '_'",
            )
        return value


class UserUpdateFormDTO(_UsernameMixin):
    """PATCH профиля через form (если понадобится отдельная ручка)."""

    username: str | None = Field(default=None, min_length=3, max_length=32)
    email: EmailStr | None = None
    birthday: date | None = None
    description: str | None = Field(default=None, max_length=512)

    @model_validator(mode="after")
    def _ensure_at_least_one_field(self) -> "UserUpdateFormDTO":
        if not self.model_dump(exclude_unset=True):
            raise ValueError("Не передано ни одного поля для обновления")
        return self

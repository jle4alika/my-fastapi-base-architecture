"""
Выходные DTO для ручек, отдающих информацию о пользователе.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from backend.api.schemas.dto.base import BaseDTO


class UserShortDTO(BaseDTO):
    """Краткое представление пользователя."""

    id: uuid.UUID
    username: str


class UserPublicDTO(UserShortDTO):
    """Публичный профиль (без email и флагов безопасности)."""

    description: str | None = None
    created_time: datetime | None = None


class UserReadDTO(UserPublicDTO):
    """Расширенное чтение (email, флаги)."""

    email: str
    birthday: str = ""
    is_active: bool
    is_verified: bool
    updated_time: datetime | None = None


class UserMeDTO(UserReadDTO):
    """Профиль текущего пользователя."""

    is_superuser: bool

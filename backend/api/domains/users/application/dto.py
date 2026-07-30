"""
Выходные DTO use-case'ов профиля.

Держим только реальные контракты ответов (не иерархию «на вырост»).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from common.schemas.base import BaseDTO


class UserPublicDTO(BaseDTO):
    """Публичный профиль (GET /profile/{id})."""

    id: uuid.UUID
    username: str
    created_at: datetime | None = None


class UserMeDTO(BaseDTO):
    """Свой профиль (GET /profile/me)."""

    id: uuid.UUID
    username: str
    email: str
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

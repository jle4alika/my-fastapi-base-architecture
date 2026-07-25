"""
Доменная сущность User — поведение и инварианты здесь.

Persistence (SQLAlchemy) и HTTP сюда не проникают: масштабирование =
добавление методов/правил в этот класс (или выделение VO позже).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar
from uuid import UUID

from domains.users.domain.errors import (
    InvalidPasswordError,
    InvalidUsernameError,
    UserInactiveError,
)

_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]+$")


@dataclass(slots=True, kw_only=True)
class User:
    """Агрегат пользователя: состояние + доменные операции."""

    MIN_PASSWORD_LENGTH: ClassVar[int] = 8
    MIN_USERNAME_LENGTH: ClassVar[int] = 3
    MAX_USERNAME_LENGTH: ClassVar[int] = 32

    id: UUID
    email: str
    username: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # --- инварианты (можно вызвать до создания сущности) ---

    @classmethod
    def validate_password(cls, password: str) -> None:
        if len(password) < cls.MIN_PASSWORD_LENGTH:
            raise InvalidPasswordError(
                f"Пароль должен быть не короче {cls.MIN_PASSWORD_LENGTH} символов",
            )

    @classmethod
    def validate_username(cls, username: str) -> None:
        if not cls.MIN_USERNAME_LENGTH <= len(username) <= cls.MAX_USERNAME_LENGTH:
            raise InvalidUsernameError(
                f"username: длина {cls.MIN_USERNAME_LENGTH}–{cls.MAX_USERNAME_LENGTH}",
            )
        if not _USERNAME_RE.fullmatch(username):
            raise InvalidUsernameError("username: только латиница, цифры и '_'")

    # --- команды ---

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False
        self.is_superuser = False

    def mark_verified(self) -> None:
        self._ensure_active()
        self.is_verified = True

    def rename(self, username: str) -> None:
        self._ensure_active()
        self.validate_username(username)
        self.username = username

    def replace_password_hash(self, hashed_password: str) -> None:
        """Хеш считается в infra; домен только принимает готовый."""
        self._ensure_active()
        if not hashed_password:
            raise InvalidPasswordError("hashed_password пуст")
        self.hashed_password = hashed_password

    def grant_superuser(self) -> None:
        self._ensure_active()
        self.is_superuser = True

    def revoke_superuser(self) -> None:
        self.is_superuser = False

    def _ensure_active(self) -> None:
        if not self.is_active:
            raise UserInactiveError("Пользователь деактивирован")

"""Доменные ошибки users."""

from __future__ import annotations

from common.exceptions.errors import AppError, NotFoundError

__all__ = [
    "AppError",
    "NotFoundError",
    "InvalidPasswordError",
    "InvalidUsernameError",
    "UserInactiveError",
]


class InvalidPasswordError(AppError):
    """Пароль не проходит доменные правила."""


class InvalidUsernameError(AppError):
    """Username не проходит доменные правила."""


class UserInactiveError(AppError):
    """Операция недоступна для неактивного пользователя."""

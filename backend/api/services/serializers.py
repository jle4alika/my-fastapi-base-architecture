"""Сборка response-DTO из ORM-модели User."""

from __future__ import annotations

from backend.api.schemas.responces.user import UserMeDTO, UserPublicDTO, UserShortDTO
from backend.database.models import User


def user_to_short(user: User) -> UserShortDTO:
    """Краткое представление пользователя."""

    return UserShortDTO(
        id=user.id,
        username=user.username,
    )


def user_to_public(user: User) -> UserPublicDTO:
    """Публичный профиль."""

    short = user_to_short(user)
    return UserPublicDTO(
        **short.model_dump(),
        description=user.description,
        created_time=user.created_time,
    )


def user_to_me(user: User) -> UserMeDTO:
    """Полный профиль текущего пользователя."""

    short = user_to_short(user)
    return UserMeDTO(
        **short.model_dump(),
        email=user.email,
        birthday=user.birthday or "",
        description=user.description,
        is_active=user.is_active,
        is_verified=user.is_verified,
        is_superuser=user.is_superuser,
        created_time=user.created_time,
        updated_time=user.updated_time,
    )

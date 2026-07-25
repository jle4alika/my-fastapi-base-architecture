"""Маппинг domain.User → DTO ответов."""

from __future__ import annotations

from domains.users.application.dto import UserMeDTO, UserPublicDTO
from domains.users.domain.entities import User


class UserMapper:
    @classmethod
    def to_public(cls, user: User) -> UserPublicDTO:
        return UserPublicDTO(
            id=user.id,
            username=user.username,
            created_at=user.created_at,
        )

    @classmethod
    def to_me(cls, user: User) -> UserMeDTO:
        return UserMeDTO(
            id=user.id,
            username=user.username,
            created_at=user.created_at,
            email=user.email,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
            updated_at=user.updated_at,
        )

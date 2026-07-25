"""ORM ↔ domain entity."""

from __future__ import annotations

from domains.users.domain.entities import User
from domains.users.infrastructure.models import UserModel


def to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        email=model.email,
        username=model.username,
        hashed_password=model.hashed_password,
        is_active=model.is_active,
        is_superuser=model.is_superuser,
        is_verified=model.is_verified,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )

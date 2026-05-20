"""
Дополнительные ручки пользователей (кэш, публичный профиль по id).

Базовые CRUD и /users/me — в роутере fastapi-users (см. api/app.py).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from backend.api.dependencies.db import db_sessions
from backend.api.dependencies.users import CurrentActiveUser
from backend.api.schemas.responces.user import UserMeDTO, UserPublicDTO
from backend.api.services.serializers import user_to_me, user_to_public
from backend.database.models import User

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=UserMeDTO)
async def get_me_cached(user: CurrentActiveUser) -> UserMeDTO:
    """Профиль текущего пользователя (с Redis-кэшем)."""

    return user_to_me(user)


@router.get("/{user_id}", response_model=UserPublicDTO)
async def get_user_public(
    user_id: uuid.UUID,
    db_session: db_sessions,
) -> UserPublicDTO:
    """Публичный профиль пользователя по UUID."""

    row = await db_session.get(User, user_id)
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_to_public(row)

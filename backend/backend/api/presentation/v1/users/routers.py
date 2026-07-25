"""Profile HTTP routes (v1).

Паттерн новой ручки:
  - response_model = DTO из domains.*.application.dto
  - логика только в service (Depends UserServiceDep)
  - domain errors → глобальные handlers в app.py
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter
from fastapi_cache.decorator import cache

from presentation.v1.users.dependencies import UserServiceDep
from core.config import settings
from domains.users.application.dto import UserMeDTO, UserPublicDTO
from domains.users.infrastructure.auth import CurrentActiveUser
from infrastructure.cache import key_builder

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=UserMeDTO)
@cache(
    expire=settings.cache.EXPIRE_SECONDS,
    namespace=settings.cache.NAMESPACE_ME,
    key_builder=key_builder,
)
async def get_me_cached(
    user: CurrentActiveUser,
    service: UserServiceDep,
) -> UserMeDTO:
    return await service.get_me_profile(user.id)


@router.get("/{user_id}", response_model=UserPublicDTO)
@cache(
    expire=settings.cache.EXPIRE_SECONDS,
    namespace=settings.cache.NAMESPACE_USER,
    key_builder=key_builder,
)
async def get_user_public(
    user_id: uuid.UUID,
    service: UserServiceDep,
) -> UserPublicDTO:
    return await service.get_public_profile(user_id)

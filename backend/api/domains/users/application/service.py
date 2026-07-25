"""Application-сервис профиля."""

from __future__ import annotations

from uuid import UUID

from domains.users.application.dto import UserMeDTO, UserPublicDTO
from domains.users.application.mappers import UserMapper
from domains.users.application.ports import AbstractUserService, AbstractUserUnitOfWork
from domains.users.domain.errors import NotFoundError


class UserService(AbstractUserService):
    def __init__(self, uow: AbstractUserUnitOfWork) -> None:
        self._uow = uow

    async def get_public_profile(self, user_id: UUID) -> UserPublicDTO:
        user = await self._uow.users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise NotFoundError("User not found")
        return UserMapper.to_public(user)

    async def get_me_profile(self, user_id: UUID) -> UserMeDTO:
        user = await self._uow.users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise NotFoundError("User not found")
        return UserMapper.to_me(user)

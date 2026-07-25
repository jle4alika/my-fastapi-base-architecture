"""
UserManager — anti-corruption adapter над fastapi-users.

Регистрация/пароли/verify идут здесь; профильные use-cases — в application.UserService.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin, exceptions
from fastapi_users.db import SQLAlchemyUserDatabase

from core.config import settings
from core.logging import get_logger
from domains.users.application.ports import AbstractUserRepository
from domains.users.domain.entities import User
from domains.users.domain.errors import InvalidPasswordError
from domains.users.infrastructure.auth_schemas import UserCreate, UserUpdate
from domains.users.infrastructure.models import UserModel
from domains.users.infrastructure.repository import UserRepository
from domains.users.infrastructure.user_db import get_user_db
from infrastructure.smtp import AbstractSmtpRepository, get_smtp_repository, smtp_repository

logger = get_logger(__name__)


class UserManager(UUIDIDMixin, BaseUserManager[UserModel, uuid.UUID]):
    """ACL: fastapi-users ↔ доменный репозиторий + SMTP."""

    def __init__(
        self,
        user_db: SQLAlchemyUserDatabase,
        smtp: AbstractSmtpRepository | None = None,
    ) -> None:
        super().__init__(user_db)
        self.reset_password_token_secret = settings.jwt.SECRET_KEY
        self.verification_token_secret = settings.jwt.SECRET_KEY
        self._smtp = smtp or smtp_repository

    @property
    def users(self) -> AbstractUserRepository:
        return UserRepository(self.user_db.session)

    async def validate_password(
        self,
        password: str,
        user: UserCreate | UserModel,
    ) -> None:
        try:
            User.validate_password(password)
        except InvalidPasswordError as exc:
            raise exceptions.InvalidPasswordException(reason=str(exc)) from exc

    async def create(
        self,
        user_create: UserCreate,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> UserModel:
        await self.validate_password(user_create.password, user_create)

        if await self.user_db.get_by_email(user_create.email) is not None:
            raise exceptions.UserAlreadyExists()

        if await self.users.is_username_taken(user_create.username):
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict() if safe else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)
        user_dict["username"] = user_create.username

        created_user = await self.user_db.create(user_dict)
        await self.on_after_register(created_user, request)
        return created_user

    async def update(
        self,
        user_update: UserUpdate,
        user: UserModel,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> UserModel:
        update_dict = (
            user_update.create_update_dict() if safe else user_update.create_update_dict_superuser()
        )

        if "username" in update_dict and await self.users.is_username_taken(
            update_dict["username"],
            exclude_id=user.id,
        ):
            raise exceptions.UserAlreadyExists()

        updated = await self.user_db.update(user, update_dict)
        await self.on_after_update(updated, update_dict, request)
        return updated

    async def on_after_register(
        self,
        user: UserModel,
        request: Optional[Request] = None,
    ) -> None:
        logger.info("Зарегистрирован пользователь id=%s email=%s", user.id, user.email)

    async def on_after_forgot_password(
        self,
        user: UserModel,
        token: str,
        request: Optional[Request] = None,
    ) -> None:
        await self._smtp.send(
            to=user.email,
            subject="Сброс пароля",
            body=(
                f"Здравствуйте, {user.username}!\n\n"
                f"Токен сброса пароля: {token}\n"
                "Если вы не запрашивали сброс — проигнорируйте это письмо.\n"
            ),
        )

    async def on_after_request_verify(
        self,
        user: UserModel,
        token: str,
        request: Optional[Request] = None,
    ) -> None:
        await self._smtp.send(
            to=user.email,
            subject="Подтверждение email",
            body=f"Здравствуйте, {user.username}!\n\nТокен верификации: {token}\n",
        )


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
    smtp: AbstractSmtpRepository = Depends(get_smtp_repository),
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db, smtp=smtp)

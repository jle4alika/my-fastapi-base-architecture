"""
UserManager: регистрация, сброс пароля, верификация, хуки событий.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import AsyncGenerator
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin, exceptions
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy import select

from backend.api.users.db import get_user_db
from backend.api.users.schemas import UserCreate, UserUpdate
from backend.database.models.user import User
from backend.project_config import settings

logger = logging.getLogger(__name__)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """
    Бизнес-логика пользователей (наследник BaseUserManager).

    Секреты токенов сброса пароля и верификации — из настроек.
    """

    reset_password_token_secret = settings.JWT_SECRET_KEY
    verification_token_secret = settings.JWT_SECRET_KEY

    async def validate_password(
        self,
        password: str,
        user: UserCreate | User,
    ) -> None:
        """Проверка сложности пароля перед созданием/сменой."""

        if len(password) < 8:
            raise exceptions.InvalidPasswordException(
                reason="Пароль должен быть не короче 8 символов",
            )

    async def create(
        self,
        user_create: UserCreate,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> User:
        """Создание пользователя с доменными полями (username, birthday, …)."""

        await self.validate_password(user_create.password, user_create)

        existing = await self.user_db.get_by_email(user_create.email)
        if existing is not None:
            raise exceptions.UserAlreadyExists()

        q = await self.user_db.session.execute(
            select(User).where(User.username == user_create.username),
        )
        if q.scalar_one_or_none() is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        user_dict["username"] = user_create.username
        user_dict["birthday"] = (
            user_create.birthday.isoformat() if user_create.birthday else ""
        )
        user_dict["description"] = user_create.description

        created_user = await self.user_db.create(user_dict)
        await self.on_after_register(created_user, request)
        return created_user

    async def update(
        self,
        user_update: UserUpdate,
        user: User,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> User:
        """Обновление с проверкой уникальности username и полей профиля."""

        update_dict = (
            user_update.create_update_dict()
            if safe
            else user_update.create_update_dict_superuser()
        )

        if "username" in update_dict:
            q = await self.user_db.session.execute(
                select(User).where(User.username == update_dict["username"]),
            )
            other = q.scalar_one_or_none()
            if other is not None and other.id != user.id:
                raise exceptions.UserAlreadyExists()

        if "birthday" in update_dict and update_dict["birthday"] is not None:
            b = update_dict["birthday"]
            update_dict["birthday"] = (
                b.isoformat() if hasattr(b, "isoformat") else str(b)
            )

        updated = await self.user_db.update(user, update_dict)
        await self.on_after_update(updated, update_dict, request)
        return updated

    async def on_after_register(
        self,
        user: User,
        request: Optional[Request] = None,
    ) -> None:
        logger.info("Зарегистрирован пользователь id=%s email=%s", user.id, user.email)

    async def on_after_forgot_password(
        self,
        user: User,
        token: str,
        request: Optional[Request] = None,
    ) -> None:
        logger.info(
            "Сброс пароля: user_id=%s (в проде отправить токен на email)",
            user.id,
        )

    async def on_after_request_verify(
        self,
        user: User,
        token: str,
        request: Optional[Request] = None,
    ) -> None:
        logger.info(
            "Верификация: user_id=%s (в проде отправить токен на email)",
            user.id,
        )


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    """Dependency: экземпляр UserManager на запрос."""

    yield UserManager(user_db)

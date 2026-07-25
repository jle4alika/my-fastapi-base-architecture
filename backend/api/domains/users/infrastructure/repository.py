"""Репозиторий: таблица users → domain.User."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from domains.users.application.ports import AbstractUserRepository
from domains.users.domain.entities import User
from domains.users.infrastructure.models import UserModel
from domains.users.infrastructure.orm_mapper import to_entity


class UserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        model = await self._session.get(UserModel, user_id)
        return to_entity(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalars().one_or_none()
        return to_entity(model) if model else None

    async def get_by_username(self, username: str) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.username == username),
        )
        model = result.scalars().one_or_none()
        return to_entity(model) if model else None

    async def is_username_taken(
        self,
        username: str,
        *,
        exclude_id: UUID | None = None,
    ) -> bool:
        query = select(func.count()).select_from(UserModel).where(UserModel.username == username)
        if exclude_id is not None:
            query = query.where(UserModel.id != exclude_id)
        result = await self._session.execute(query)
        return int(result.scalar_one()) > 0

    async def list_active(self, *, limit: int = 50, offset: int = 0) -> list[User]:
        result = await self._session.execute(
            select(UserModel)
            .where(UserModel.is_active.is_(True))
            .order_by(UserModel.created_at.desc())
            .limit(limit)
            .offset(offset),
        )
        return [to_entity(m) for m in result.scalars().all()]

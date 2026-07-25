"""Порты application-слоя users."""

from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self
from uuid import UUID

from domains.users.application.dto import UserMeDTO, UserPublicDTO
from domains.users.domain.entities import User


class AbstractUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    async def is_username_taken(
        self,
        username: str,
        *,
        exclude_id: UUID | None = None,
    ) -> bool: ...

    @abstractmethod
    async def list_active(self, *, limit: int = 50, offset: int = 0) -> list[User]: ...


class AbstractUserUnitOfWork(ABC):
    users: AbstractUserRepository

    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...


class AbstractUserService(ABC):
    @abstractmethod
    async def get_public_profile(self, user_id: UUID) -> UserPublicDTO: ...

    @abstractmethod
    async def get_me_profile(self, user_id: UUID) -> UserMeDTO: ...

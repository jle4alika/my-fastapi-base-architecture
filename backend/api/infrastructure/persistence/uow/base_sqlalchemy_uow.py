from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession


class BaseUnitOfWork(ABC):
    """
    Unit of Work над AsyncSession.

    Жизненный цикл сессии снаружи (FastAPI Depends / тесты).
    UoW только commit/rollback; сессию не закрывает.
    """

    _session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self._session.rollback()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

    @property
    def session(self) -> AsyncSession:
        return self._session

    @abstractmethod
    def _uow_marker(self) -> None:
        """Маркер: запрещает инстанцировать базовый класс."""

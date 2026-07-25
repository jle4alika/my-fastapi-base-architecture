"""Тесты UserManager (ACL)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi_users import exceptions

from domains.users.infrastructure.auth_schemas import UserCreate
from domains.users.infrastructure.manager import UserManager
from domains.users.infrastructure.repository import UserRepository
from tests.seeder import make_user_model


def _manager(*, smtp: MagicMock | None = None) -> UserManager:
    user_db = MagicMock()
    user_db.session = MagicMock()
    return UserManager(user_db, smtp=smtp or AsyncMock())


@pytest.mark.asyncio
async def test_validate_password_too_short() -> None:
    manager = _manager()
    with pytest.raises(exceptions.InvalidPasswordException):
        await manager.validate_password("short", make_user_model())


@pytest.mark.asyncio
async def test_create_raises_when_username_taken() -> None:
    manager = _manager()
    manager.user_db.get_by_email = AsyncMock(return_value=None)
    payload = UserCreate(
        email="new@example.com",
        password="password123",
        username="taken",
    )
    with patch.object(UserRepository, "is_username_taken", new=AsyncMock(return_value=True)):
        with pytest.raises(exceptions.UserAlreadyExists):
            await manager.create(payload)


@pytest.mark.asyncio
async def test_create_ok() -> None:
    manager = _manager()
    created = make_user_model(username="fresh")
    manager.user_db.get_by_email = AsyncMock(return_value=None)
    manager.user_db.create = AsyncMock(return_value=created)
    manager.on_after_register = AsyncMock()  # type: ignore[method-assign]

    payload = UserCreate(
        email="fresh@example.com",
        password="password123",
        username="fresh",
    )
    with patch.object(UserRepository, "is_username_taken", new=AsyncMock(return_value=False)):
        user = await manager.create(payload)

    assert user.username == "fresh"
    assert manager.user_db.create.await_args.args[0]["username"] == "fresh"
    assert "birthday" not in manager.user_db.create.await_args.args[0]
    assert "description" not in manager.user_db.create.await_args.args[0]


@pytest.mark.asyncio
async def test_forgot_password_sends_smtp() -> None:
    smtp = AsyncMock()
    manager = _manager(smtp=smtp)
    user = make_user_model(username="mail")
    await manager.on_after_forgot_password(user, "token-xyz")
    smtp.send.assert_awaited_once()
    assert "token-xyz" in smtp.send.await_args.kwargs["body"]

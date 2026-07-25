from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import AsyncClient

from presentation.v1.users.dependencies import get_user_service
from domains.users.application.ports import AbstractUserService
from domains.users.domain.errors import NotFoundError


@pytest.mark.asyncio
async def test_uncaught_not_found_returns_404(client: AsyncClient, app) -> None:
    service = AsyncMock(spec=AbstractUserService)
    service.get_public_profile = AsyncMock(side_effect=NotFoundError("missing"))
    app.dependency_overrides[get_user_service] = lambda: service

    response = await client.get(f"/api/v1/profile/{uuid4()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "missing"

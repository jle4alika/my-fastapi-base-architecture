"""
Аутентификация fastapi-users: JWT (Bearer + Cookie), FastAPIUsers, current_user.
"""

from __future__ import annotations

import uuid

from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
    JWTStrategy,
)

from backend.api.users.manager import get_user_manager
from backend.database.models.user import User
from backend.project_config import settings

# --- Transports: как токен передаётся в запросе ---
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

cookie_transport = CookieTransport(
    cookie_name="fastapiusersauth",
    cookie_max_age=settings.jwt_lifetime_seconds,
    cookie_httponly=True,
    cookie_samesite="lax",
)


def get_jwt_strategy() -> JWTStrategy:
    """Стратегия JWT: подпись и время жизни access-токена."""

    return JWTStrategy(
        secret=settings.JWT_SECRET_KEY,
        lifetime_seconds=settings.jwt_lifetime_seconds,
    )


# --- Backends: transport + strategy ---
auth_backend_jwt = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

auth_backend_cookie = AuthenticationBackend(
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend_jwt, auth_backend_cookie],
)

# Зависимости для защищённых ручек
current_user = fastapi_users.current_user()
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
current_verified_user = fastapi_users.current_user(active=True, verified=True)

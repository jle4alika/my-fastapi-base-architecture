"""
Пакет fastapi-users: схемы, менеджер, аутентификация, адаптер БД.
"""

from backend.api.users.auth import (
    auth_backend_cookie,
    auth_backend_jwt,
    current_active_user,
    current_superuser,
    current_user,
    current_verified_user,
    fastapi_users,
)
from backend.api.users.db import get_user_db
from backend.api.users.manager import UserManager, get_user_manager
from backend.api.users.schemas import UserCreate, UserRead, UserUpdate

__all__ = [
    "UserCreate",
    "UserRead",
    "UserUpdate",
    "UserManager",
    "get_user_db",
    "get_user_manager",
    "fastapi_users",
    "auth_backend_jwt",
    "auth_backend_cookie",
    "current_user",
    "current_active_user",
    "current_superuser",
    "current_verified_user",
]

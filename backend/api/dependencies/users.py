"""
Зависимости FastAPI для текущего пользователя (fastapi-users).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from backend.api.users.auth import (
    current_active_user as _current_active_user,
    current_superuser as _current_superuser,
    current_user as _current_user,
)
from backend.database.models.user import User

CurrentUser = Annotated[User, Depends(_current_user)]
CurrentActiveUser = Annotated[User, Depends(_current_active_user)]
CurrentSuperuser = Annotated[User, Depends(_current_superuser)]

# Алиас для совместимости
current_user = CurrentActiveUser
current_active_user = CurrentActiveUser

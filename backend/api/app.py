"""
Точка входа FastAPI: lifespan, middleware, роутеры fastapi-users.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from backend.api.routers import main_router
from backend.api.services.redis.rate_limiter import rate_limit_middleware, redis_lifespan
from backend.api.users import (
    UserCreate,
    UserRead,
    UserUpdate,
    auth_backend_cookie,
    auth_backend_jwt,
    fastapi_users,
)
from backend.database.schema_bootstrap import bootstrap_schema
from backend.project_config import configure_logging, settings

_MEDIA_ROOT = Path(settings.MEDIA_UPLOAD_DIR).resolve()
_MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("uvicorn.error")

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Старт: Redis, таблицы БД. Стоп: закрытие Redis."""

    async with redis_lifespan(app):
        await bootstrap_schema()
        yield


app = FastAPI(
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    title="FastAPI Architecture Template",
    description="Шаблон API с fastapi-users, SQLAlchemy, Redis, RabbitMQ",
)

app.middleware("http")(rate_limit_middleware)

# --- Роутеры fastapi-users (аутентификация и пользователи) ---
app.include_router(
    fastapi_users.get_auth_router(auth_backend_jwt),
    prefix="/api/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_auth_router(auth_backend_cookie),
    prefix="/api/auth/cookie",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/api/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/api/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/api/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/api/users",
    tags=["users"],
)

# --- Дополнительные доменные ручки (кэш, публичный профиль) ---
app.include_router(main_router, prefix="/api")

app.mount(
    "/media/files",
    StaticFiles(directory=str(_MEDIA_ROOT)),
    name="media_files",
)

Instrumentator().instrument(app).expose(app)


if __name__ == "__main__":
    uvicorn.run(
        "backend.api.app:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )

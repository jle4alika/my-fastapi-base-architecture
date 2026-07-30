"""
Точка входа FastAPI: lifespan, middlewares, роутеры.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from presentation.v1.router import api_v1_router
from common.exceptions.base_handler import (
    app_error_handler,
    global_500_handler,
    not_found_handler,
)
from common.exceptions.errors import AppError, NotFoundError
from core.logging import configure_logging, get_logger
from domains.users.infrastructure.auth import (
    auth_backend_cookie,
    auth_backend_jwt,
    fastapi_users,
)
from domains.users.infrastructure.auth_schemas import (
    UserCreate,
    UserRead,
    UserUpdate,
)
from infrastructure.dependencies.rate_limiter import rate_limiter_factory
from infrastructure.postgres.schema_bootstrap import bootstrap_schema
from infrastructure.redis.rate_limiter import rate_limit_middleware, redis_lifespan

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
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
app.add_exception_handler(NotFoundError, not_found_handler)
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, global_500_handler)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


API_V1_PREFIX = "/api/v1"

app.include_router(
    fastapi_users.get_auth_router(auth_backend_jwt),
    prefix=f"{API_V1_PREFIX}/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_auth_router(auth_backend_cookie),
    prefix=f"{API_V1_PREFIX}/auth/cookie",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix=f"{API_V1_PREFIX}/auth",
    tags=["auth"],
    dependencies=[Depends(rate_limiter_factory("register", 10, 3600))],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix=f"{API_V1_PREFIX}/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix=f"{API_V1_PREFIX}/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix=f"{API_V1_PREFIX}/users",
    tags=["users"],
)

app.include_router(api_v1_router, prefix=API_V1_PREFIX)

Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    excluded_handlers=["/metrics", "/health"],
).instrument(app).expose(app, include_in_schema=False)


if __name__ == "__main__":
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )

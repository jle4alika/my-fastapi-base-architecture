"""
Redis: кэш fastapi-cache2, rate limiting (pyrate_limiter), middleware.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from functools import lru_cache
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from pyrate_limiter import Duration, Limiter, Rate
from pyrate_limiter.buckets import RedisBucket
from redis.asyncio import Redis
from starlette.responses import Response

from backend.project_config import configure_logging, settings

configure_logging()

rate_limiter: Limiter | None = None
_named_limiters: dict[str, Limiter] = {}


@lru_cache
def get_redis() -> Redis:
    """Клиент Redis (bytes; совместим с fastapi-cache и pyrate_limiter)."""

    return Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=False,
    )


async def _get_or_create_named_limiter(
    scope: str,
    limit: int,
    window_seconds: int,
) -> Limiter:
    """Лимитер с именованным scope (для Depends на отдельных ручках)."""

    cache_key = f"{scope}:{limit}:{window_seconds}"
    if cache_key in _named_limiters:
        return _named_limiters[cache_key]

    redis = get_redis()
    rates = [Rate(limit, Duration.SECOND * window_seconds)]
    bucket = await RedisBucket.init(rates, redis, f"rate-limit:{scope}")
    limiter = Limiter(bucket)
    _named_limiters[cache_key] = limiter
    return limiter


def rate_limiter_factory(
    scope: str,
    limit: int,
    window_seconds: int,
) -> Callable:
    """
    FastAPI dependency: не более `limit` запросов за `window_seconds` на IP.

    Пример: dependencies=[Depends(rate_limiter_factory("register", 10, 3600))]
    """

    async def _check(request: Request) -> None:
        limiter = await _get_or_create_named_limiter(scope, limit, window_seconds)
        client_ip = request.client.host if request.client else "unknown"
        key = f"{scope}:{client_ip}"
        allowed = await limiter.try_acquire_async(key, blocking=False)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Too Many Requests. Превышен лимит запросов.",
            )

    return _check


@asynccontextmanager
async def redis_lifespan(app: FastAPI):
    """Lifespan: ping Redis, инициализация кэша и глобального лимитера."""

    global rate_limiter

    redis = get_redis()
    redis_enabled = False

    try:
        logging.info("Проверка соединения с Redis...")
        await redis.ping()
        logging.info("Redis работает")
        redis_enabled = True
    except Exception as exc:
        if settings.REDIS_OPTIONAL:
            logging.warning(
                "Redis недоступен (%s): кэш и rate limit отключены",
                exc,
            )
        else:
            raise

    if redis_enabled:
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
        rates = [Rate(50, Duration.SECOND * 5)]
        redis_bucket = await RedisBucket.init(rates, redis, "api-rate-limits")
        rate_limiter = Limiter(redis_bucket)

    yield

    if redis_enabled:
        await redis.aclose()
        _named_limiters.clear()
        logging.info("Redis отключен")


def get_rate_limiter() -> Limiter | None:
    return rate_limiter


_RATE_LIMIT_SKIP_PREFIXES = (
    "/metrics",
    "/api/docs",
    "/api/openapi.json",
    "/media/",
)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


async def rate_limit_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Глобальный лимит: 50 запросов / 5 с на IP+path."""

    path = request.url.path
    if path.startswith(_RATE_LIMIT_SKIP_PREFIXES):
        return await call_next(request)

    limiter = get_rate_limiter()
    if limiter is None:
        return await call_next(request)

    rate_limit_key = f"{_client_ip(request)}:{path}"
    allowed = await limiter.try_acquire_async(rate_limit_key, blocking=False)
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too Many Requests. Превышен лимит запросов."},
        )

    return await call_next(request)

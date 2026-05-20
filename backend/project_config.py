"""
Конфигурация приложения через переменные окружения (pydantic-settings).

Плоские имена полей совпадают с backend/.env (DB_HOST, JWT_SECRET_KEY и т.д.).
"""

from __future__ import annotations

import logging
from pathlib import Path
from urllib.parse import quote_plus

import pika
from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT = Path(__file__).resolve().parent


def configure_logging(level: int = logging.INFO) -> None:
    """Настраивает корневой logging для консоли."""

    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format=(
            "[%(asctime)s.%(msecs)03d] %(funcName)20s "
            "%(module)s:%(lineno)d %(levelname)-8s - %(message)s"
        ),
        handlers=[logging.StreamHandler()],
    )


def _env_files() -> tuple[str, ...]:
    """backend/.env и при необходимости .env в корне репозитория."""

    paths = (_ROOT / ".env", _ROOT.parent / ".env")
    return tuple(str(p) for p in paths if p.is_file())


class Settings(BaseSettings):
    """Переменные окружения API (см. backend/.env.example)."""

    model_config = SettingsConfigDict(
        env_file=_env_files() or None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Безопасность / JWT (fastapi-users) ---
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_USE_LONG_SECRET"
    JWT_ACCESS_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    # --- База данных ---
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASS: str = "postgres"
    DB_NAME: str = "fastapi_architecture"
    TEST_DATABASE_URL: str | None = None
    USE_SQLITE: bool = True
    USE_PGBOUNCER: bool = False
    DB_DIRECT_HOST: str | None = None
    DB_DIRECT_PORT: int | None = None
    DB_RESET_ON_LEGACY_PK: bool = False
    # true: при старте API выполнить `alembic upgrade head`
    DB_MIGRATE_ON_STARTUP: bool = False
    # true: create_all при старте (только dev, если миграции не гоняете)
    DB_CREATE_ALL_ON_STARTUP: bool = False

    # --- Redis ---
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    # true: при недоступном Redis API стартует без кэша и rate limit
    REDIS_OPTIONAL: bool = True

    # --- RabbitMQ ---
    RMQ_HOST: str = "localhost"
    RMQ_PORT: int = 5672
    RMQ_LOGIN: str = "guest"
    RMQ_PASS: str = "guest"

    # --- Утилиты ---
    MEDIA_UPLOAD_DIR: str = "uploads"
    MEDIA_MAX_BYTES: int = 20 * 1024 * 1024

    # --- Кэш (fastapi-cache2) ---
    CACHE_NAMESPACE_ME: str = "me"
    CACHE_NAMESPACE_USER: str = "get-user"

    @property
    def jwt_lifetime_seconds(self) -> int:
        """Срок жизни access JWT в секундах."""

        return self.JWT_ACCESS_EXPIRE_MINUTES * 60

    @property
    def DATABASE_URL_asyncpg(self) -> str:
        """URL asyncpg для PostgreSQL."""

        user = quote_plus(self.DB_USER)
        pwd = quote_plus(self.DB_PASS)
        return (
            f"postgresql+asyncpg://{user}:{pwd}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def DATABASE_URL_sqlite(self) -> str:
        """URL aiosqlite для локальной разработки."""

        return f"sqlite+aiosqlite:///{self.DB_NAME}.sqlite"


settings = Settings()


def get_rmq_connection() -> pika.BlockingConnection:
    """Синхронное соединение с RabbitMQ (pika, воркеры/скрипты)."""

    return pika.BlockingConnection(
        pika.ConnectionParameters(
            host=settings.RMQ_HOST,
            port=settings.RMQ_PORT,
            credentials=pika.PlainCredentials(settings.RMQ_LOGIN, settings.RMQ_PASS),
        )
    )


def get_rmq_url() -> str:
    """URL для aio-pika: amqp://user:pass@host:port/."""

    user = quote_plus(settings.RMQ_LOGIN)
    pwd = quote_plus(settings.RMQ_PASS)
    return f"amqp://{user}:{pwd}@{settings.RMQ_HOST}:{settings.RMQ_PORT}/"

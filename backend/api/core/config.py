"""
Конфигурация приложения через переменные окружения (pydantic-settings).
Плоские имена полей в .env совпадают с префиксами вложенных классов.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote_plus

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT = Path(__file__).resolve().parent.parent

_DEFAULT_JWT_SECRET = "CHANGE_ME_IN_PRODUCTION_USE_LONG_SECRET"


def _env_files() -> tuple[str, ...]:
    """backend/.env и при необходимости .env в корне репозитория."""
    paths = (_ROOT / ".env", _ROOT.parent / ".env")
    return tuple(str(p) for p in paths if p.is_file())


_ENV_FILE_KWARGS = {
    "env_file": _env_files() or None,
    "env_file_encoding": "utf-8",
    "extra": "ignore",
}


class JWTSettings(BaseSettings):
    """JWT / fastapi-users (переменные JWT_*)."""

    model_config = SettingsConfigDict(env_prefix="JWT_", **_ENV_FILE_KWARGS)

    SECRET_KEY: str = _DEFAULT_JWT_SECRET
    ACCESS_EXPIRE_MINUTES: int = 30

    @property
    def lifetime_seconds(self) -> int:
        return self.ACCESS_EXPIRE_MINUTES * 60


class DatabaseSettings(BaseSettings):
    """Настройки PostgreSQL (переменные DB_*)."""

    model_config = SettingsConfigDict(env_prefix="DB_", **_ENV_FILE_KWARGS)

    HOST: str = "localhost"
    PORT: int = 5432
    USER: str = "postgres"
    PASS: str = "postgres"
    NAME: str = "fastapi_architecture"
    TEST_URL: str | None = None
    USE_PGBOUNCER: bool = False
    DIRECT_HOST: str | None = None
    DIRECT_PORT: int | None = None
    MIGRATE_ON_STARTUP: bool = False
    CREATE_ALL_ON_STARTUP: bool = False

    @property
    def url_asyncpg(self) -> str:
        user = quote_plus(self.USER)
        pwd = quote_plus(self.PASS)
        return f"postgresql+asyncpg://{user}:{pwd}@{self.HOST}:{self.PORT}/{self.NAME}"


class RedisSettings(BaseSettings):
    """Redis (переменные REDIS_*)."""

    model_config = SettingsConfigDict(env_prefix="REDIS_", **_ENV_FILE_KWARGS)

    HOST: str = "localhost"
    PORT: int = 6379
    OPTIONAL: bool = True

    @property
    def url(self) -> str:
        """URL для клиентов (кэш и т.п.), DB 0."""
        return f"redis://{self.HOST}:{self.PORT}/0"

    @property
    def celery_result_url(self) -> str:
        """URL result backend Celery (отдельная DB, чтобы не пересекаться с кэшем)."""
        return f"redis://{self.HOST}:{self.PORT}/1"


class RabbitMQSettings(BaseSettings):
    """RabbitMQ (переменные RMQ_*)."""

    model_config = SettingsConfigDict(env_prefix="RMQ_", **_ENV_FILE_KWARGS)

    HOST: str = "localhost"
    PORT: int = 5672
    LOGIN: str = "guest"
    PASS: str = "guest"

    @property
    def url(self) -> str:
        user = quote_plus(self.LOGIN)
        pwd = quote_plus(self.PASS)
        return f"amqp://{user}:{pwd}@{self.HOST}:{self.PORT}/"

    @property
    def celery_broker_url(self) -> str:
        """Broker URL для Celery (vhost /)."""
        user = quote_plus(self.LOGIN)
        pwd = quote_plus(self.PASS)
        return f"amqp://{user}:{pwd}@{self.HOST}:{self.PORT}//"


class CelerySettings(BaseSettings):
    """Celery (переменные CELERY_*). Broker — RabbitMQ, results — Redis."""

    model_config = SettingsConfigDict(env_prefix="CELERY_", **_ENV_FILE_KWARGS)

    BROKER_URL: str | None = None
    RESULT_BACKEND: str | None = None
    TASK_ALWAYS_EAGER: bool = False
    WORKER_CONCURRENCY: int = 2
    TASK_DEFAULT_QUEUE: str = "celery"


class CacheSettings(BaseSettings):
    """Кэш fastapi-cache2 (переменные CACHE_*)."""

    model_config = SettingsConfigDict(env_prefix="CACHE_", **_ENV_FILE_KWARGS)

    NAMESPACE_ME: str = "me"
    NAMESPACE_USER: str = "get-user"
    EXPIRE_SECONDS: int = 60


class SmtpSettings(BaseSettings):
    """SMTP (переменные SMTP_*)."""

    model_config = SettingsConfigDict(env_prefix="SMTP_", **_ENV_FILE_KWARGS)

    ENABLED: bool = False
    HOST: str = "localhost"
    PORT: int = 587
    USER: str = ""
    PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@example.com"
    USE_TLS: bool = True
    TIMEOUT: int = 30


class Settings(BaseSettings):
    """Переменные окружения API (см. backend/.env.example)."""

    model_config = SettingsConfigDict(**_ENV_FILE_KWARGS)

    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    # Доверять X-Forwarded-For только за reverse-proxy (nginx)
    TRUST_PROXY_HEADERS: bool = False

    jwt: JWTSettings = Field(default_factory=JWTSettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    rmq: RabbitMQSettings = Field(default_factory=RabbitMQSettings)
    celery: CelerySettings = Field(default_factory=CelerySettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    smtp: SmtpSettings = Field(default_factory=SmtpSettings)

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() in {"prod", "production"}

    @model_validator(mode="after")
    def _reject_default_jwt_in_production(self) -> Settings:
        if self.is_production and self.jwt.SECRET_KEY == _DEFAULT_JWT_SECRET:
            raise ValueError(
                "JWT_SECRET_KEY must be set to a strong secret in production",
            )
        return self


settings = Settings()

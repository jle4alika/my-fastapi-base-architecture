# FastAPI Architecture Template

Шаблон backend API: **FastAPI**, **fastapi-users**, **SQLAlchemy 2 async**, **Redis**, **RabbitMQ**.

Документация fastapi-users: [Configuration Overview](https://fastapi-users.github.io/fastapi-users/10.1/configuration/overview/)  
В проекте установлена **v13** (совместимость с Pydantic v2 / email-validator ≥ 2); API роутеров совпадает с документацией 10.x.

## Быстрый старт (SQLite, без Docker)

```bash
cd backend
cp .env.example .env

cd ..
make -C backend migrate
PYTHONPATH=. USE_SQLITE=true uvicorn backend.api.app:app --reload --port 8000
```

## Миграции (Alembic)

Конфиг: `backend/alembic.ini`, скрипты: `backend/alembic/versions/`.

| Команда | Действие |
|---------|----------|
| `make -C backend migrate` | `alembic upgrade head` |
| `make -C backend revision msg="описание"` | autogenerate новой миграции |
| `make -C backend migrate-down` | откат на 1 ревизию |
| `make -C backend current` | текущая ревизия |

Для PostgreSQL: `USE_SQLITE=false` в `.env` и те же команды (URL берётся из `project_config`).

При добавлении моделей импортируйте их в `backend/alembic/env.py`, иначе autogenerate их не увидит.

Опции в `.env`:

- `DB_MIGRATE_ON_STARTUP=true` — `upgrade head` при старте API
- `DB_CREATE_ALL_ON_STARTUP=true` — `create_all` без Alembic (только dev)

Swagger: http://127.0.0.1:8000/api/docs

## Аутентификация (fastapi-users)

| Метод | Путь | Описание |
|--------|------|----------|
| POST | `/api/auth/register` | Регистрация |
| POST | `/api/auth/jwt/login` | Логин (Bearer JWT) |
| POST | `/api/auth/jwt/logout` | Выход |
| POST | `/api/auth/cookie/login` | Логин (cookie) |
| POST | `/api/auth/forgot-password` | Запрос сброса пароля |
| POST | `/api/auth/reset-password` | Сброс пароля по токену |
| POST | `/api/auth/request-verify-token` | Запрос верификации email |
| POST | `/api/auth/verify` | Подтверждение email |
| GET/PATCH/DELETE | `/api/users/me` | Текущий пользователь |
| GET | `/api/users/{id}` | Пользователь по id (суперпользователь) |

Дополнительно: `/api/profile/me`, `/api/profile/{user_id}`.

## Структура

```
backend/
  api/
    app.py              # FastAPI + роутеры fastapi-users
    users/              # schemas, manager, auth backends
    routers/            # доменные ручки
    dependencies/       # DB, current user
  alembic/              # миграции Alembic
  database/
    models/user.py      # SQLAlchemy + SQLAlchemyBaseUserTableUUID
  project_config.py     # настройки из .env
```

## Docker

```bash
cd backend && docker compose up -d
```

PostgreSQL + Redis — см. `docker-compose.yml` и `.env.example`.

# Запуск из корня репозитория (Poetry)

REPO_ROOT := $(abspath .)
POETRY := poetry
ENV_FILE := --env-file backend/.env

COMPOSE_INFRA := docker compose $(ENV_FILE) -f backend/deploy/compose.infra.yml
COMPOSE_DEV := docker compose $(ENV_FILE) -f backend/deploy/compose.dev.yml
COMPOSE_PROD := docker compose $(ENV_FILE) -f backend/deploy/compose.prod.yml

.PHONY: install install-dev infra infra-down up up-dev up-dev-celery up-prod up-prod-celery \
	down down-dev down-prod logs migrate revision migrate-down current celery-worker lint format test

# --- Зависимости ---
install:
	$(POETRY) install --only main

install-dev:
	$(POETRY) install

# --- Инфра без API (локальный uvicorn) ---
infra:
	$(COMPOSE_INFRA) up -d

infra-down:
	$(COMPOSE_INFRA) down

# --- Полный стек (Celery выключен по умолчанию) ---
up: up-dev

up-dev:
	$(COMPOSE_DEV) up --build -d

up-dev-celery:
	COMPOSE_PROFILES=celery $(COMPOSE_DEV) up --build -d

up-prod:
	$(COMPOSE_PROD) up --build -d

up-prod-celery:
	COMPOSE_PROFILES=celery $(COMPOSE_PROD) up --build -d

down: down-dev

down-dev:
	$(COMPOSE_DEV) down

down-prod:
	$(COMPOSE_PROD) down

logs:
	$(COMPOSE_DEV) logs -f --tail 300

# --- Миграции / Celery / тесты на хосте ---
migrate:
	cd $(REPO_ROOT) && $(POETRY) run alembic -c backend/alembic.ini upgrade head

revision:
	cd $(REPO_ROOT) && $(POETRY) run alembic -c backend/alembic.ini revision --autogenerate -m "$(msg)"

migrate-down:
	cd $(REPO_ROOT) && $(POETRY) run alembic -c backend/alembic.ini downgrade -1

current:
	cd $(REPO_ROOT) && $(POETRY) run alembic -c backend/alembic.ini current

celery-worker:
	cd $(REPO_ROOT) && $(POETRY) run celery -A infrastructure.celery_workers.celery_app:celery_app worker --loglevel=INFO -E

lint:
	$(POETRY) run black --check backend/api backend/tests
	$(POETRY) run lint-imports

format:
	$(POETRY) run black backend/api backend/tests

test:
	$(POETRY) run pytest -q --cov=domains --cov=common --cov-report=term-missing

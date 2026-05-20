# Команды из каталога backend/ (или: make -C backend <target>)
# Корень репозитория должен быть родителем backend/ для PYTHONPATH.

REPO_ROOT := $(abspath ..)
VENV_PYTHON := $(REPO_ROOT)/.venv/bin/python
PYTHON := $(if $(wildcard $(VENV_PYTHON)),$(VENV_PYTHON),python3)
export PYTHONPATH := $(REPO_ROOT)
ALEMBIC := $(PYTHON) -m alembic -c backend/alembic.ini
ENV_SQLITE := USE_SQLITE=true DB_NAME=fastapi_architecture

.PHONY: up down logs migrate revision migrate-down current

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f --tail 300

# Применить все миграции
migrate:
	cd $(REPO_ROOT) && $(ENV_SQLITE) $(ALEMBIC) upgrade head

# Новая autogenerate-миграция: make revision msg="add posts table"
revision:
	cd $(REPO_ROOT) && $(ENV_SQLITE) $(ALEMBIC) revision --autogenerate -m "$(msg)"

# Откат на одну ревизию
migrate-down:
	cd $(REPO_ROOT) && $(ENV_SQLITE) $(ALEMBIC) downgrade -1

# Текущая ревизия
current:
	cd $(REPO_ROOT) && $(ENV_SQLITE) $(ALEMBIC) current

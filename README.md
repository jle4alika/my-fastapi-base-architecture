# FastAPI Architecture

Шаблон с onion-слоями. **Как добавить новые ручки:**  
→ [docs/ADDING_A_FEATURE.md](docs/ADDING_A_FEATURE.md)

Полный README: [backend/README.md](backend/README.md) · слои: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

```bash
poetry install
cp backend/.env.example backend/.env
make infra && make migrate
poetry run uvicorn backend.api.app:app --reload --port 8000
```

Эталон фичи в коде: `backend/api/domains/users` + `backend/api/presentation/v1/users`.

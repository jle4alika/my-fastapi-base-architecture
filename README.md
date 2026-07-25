# FastAPI Architecture

Шаблон backend — в папке [`backend/`](backend/).  
Скопируй её в свой сервис и поднимай бек оттуда.

```bash
cd backend
cp .env.example .env
poetry install
make infra && make migrate
poetry run uvicorn backend.api.app:app --reload --port 8000
```

Документация: [backend/README.md](backend/README.md) · [backend/docs/ADDING_A_FEATURE.md](backend/docs/ADDING_A_FEATURE.md)

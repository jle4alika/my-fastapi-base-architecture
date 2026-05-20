"""
Сборка дополнительных API-роутеров (поверх fastapi-users).
"""

from fastapi import APIRouter

from backend.api.routers import user

main_router = APIRouter()

main_router.include_router(user.router)

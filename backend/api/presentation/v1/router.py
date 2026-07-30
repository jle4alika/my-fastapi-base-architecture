from fastapi import APIRouter

from presentation.v1.users.routers import router as users_profile_router

api_v1_router = APIRouter()
api_v1_router.include_router(users_profile_router)

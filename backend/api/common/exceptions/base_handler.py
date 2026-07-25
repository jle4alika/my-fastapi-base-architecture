from fastapi import Request
from fastapi.responses import JSONResponse

from common.exceptions.errors import AppError, NotFoundError
from core.logging import get_logger

logger = get_logger(__name__)


async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc) or "Not found"},
    )


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc) or "Application error"},
    )


async def global_500_handler(request: Request, exc: Exception) -> JSONResponse:
    """Глобальный обработчик непредвиденных ошибок."""
    logger.error(
        "unhandled_error",
        path=str(request.url.path),
        error=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера. Пожалуйста, попробуйте позже."},
    )

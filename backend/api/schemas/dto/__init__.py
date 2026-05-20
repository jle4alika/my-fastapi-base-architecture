"""Re-export входных DTO шаблона."""

from backend.api.schemas.dto.base import BaseDTO
from backend.api.schemas.dto.user import UserUpdateFormDTO

__all__ = [
    "BaseDTO",
    "UserUpdateFormDTO",
]

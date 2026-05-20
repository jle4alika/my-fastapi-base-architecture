"""
Базовый DTO-класс с общей конфигурацией Pydantic для всех схем проекта.

`from_attributes=True` позволяет инициализировать модель из ORM-объектов
(`UserReadDTO.model_validate(user_orm)`), `str_strip_whitespace=True`
убирает крайние пробелы во всех строковых полях входящих DTO.
"""

from pydantic import BaseModel, ConfigDict


class BaseDTO(BaseModel):
    """Базовый DTO для всех Pydantic-схем сервиса."""

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        populate_by_name=True,
    )

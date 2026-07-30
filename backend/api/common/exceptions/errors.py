"""Доменные/общие ошибки приложения (не HTTP)."""

from __future__ import annotations


class NotFoundError(Exception):
    """Сущность не найдена."""


class AppError(Exception):
    """Базовая ошибка приложения."""

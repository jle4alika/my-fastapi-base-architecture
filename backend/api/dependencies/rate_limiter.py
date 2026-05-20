"""
Rate limit через pyrate_limiter (см. api/services/redis/rate_limiter.py).

Для лимита на конкретную ручку используйте:
  Depends(rate_limiter_factory("scope", limit, window_seconds))
"""

from backend.api.services.redis.rate_limiter import rate_limiter_factory

__all__ = ["rate_limiter_factory"]

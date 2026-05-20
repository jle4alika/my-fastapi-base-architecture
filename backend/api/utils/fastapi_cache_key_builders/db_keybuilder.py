from fastapi import Response, Request

import hashlib
from typing import Any, Callable, Dict, Optional, Tuple, get_args

from backend.api.dependencies.db import db_sessions


def _is_excluded(value: object, exclude_type: object) -> bool:
    """Annotated[AsyncSession, Depends(...)] нельзя передать в isinstance (Py 3.12+)."""
    inner = get_args(exclude_type)
    if inner and isinstance(value, inner[0]):
        return True
    try:
        return isinstance(value, (exclude_type,))
    except TypeError:
        return False


def key_builder(
    func: Callable[..., Any],
    namespace: str,
    *,
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
) -> str:
    exclude_types = (db_sessions,)
    cache_kw = {}
    for name, value in kwargs.items():
        if any(_is_excluded(value, t) for t in exclude_types):
            continue
        cache_kw[name] = value

    cache_key = hashlib.md5(  # noqa: S324
        f"{func.__module__}:{func.__name__}:{args}:{cache_kw}".encode()
    ).hexdigest()

    return f"{namespace}:{cache_key}"

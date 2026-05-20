"""Общие типы для API-схем."""

from __future__ import annotations

import uuid
from typing import Annotated

from pydantic import Field

UUID_ID = Annotated[uuid.UUID, Field(description="UUID сущности")]

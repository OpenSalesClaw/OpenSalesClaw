"""Shared Pydantic base schemas for standard audit/metadata fields."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class StandardReadFields(BaseModel):
    """Mixin providing the standard audit/metadata fields for all *Read schemas."""

    model_config = ConfigDict(from_attributes=True)

    sfid: str | None = None
    custom_fields: dict[str, Any] = {}
    owner_id: int | None = None
    created_by_id: int | None = None
    updated_by_id: int | None = None
    created_at: datetime
    updated_at: datetime

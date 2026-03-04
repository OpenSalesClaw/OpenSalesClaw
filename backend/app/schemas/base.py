"""Shared Pydantic base schemas for standard audit/metadata fields."""

from datetime import UTC, datetime
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict


def _ensure_tz(v: Any) -> Any:
    """Coerce naive datetimes to UTC; pass through timezone-aware ones unchanged."""
    if isinstance(v, datetime) and v.tzinfo is None:
        return v.replace(tzinfo=UTC)
    return v


# Annotated type for use in any schema that needs TZ-aware datetime inputs.
TZAwareDatetime = Annotated[datetime, BeforeValidator(_ensure_tz)]


class StandardReadFields(BaseModel):
    """Mixin providing the standard audit/metadata fields for all *Read schemas."""

    model_config = ConfigDict(from_attributes=True)

    sfid: str | None = None
    custom_fields: dict[str, Any] = {}
    owner_id: int | None = None
    created_by_id: int | None = None
    updated_by_id: int | None = None
    created_at: TZAwareDatetime
    updated_at: TZAwareDatetime

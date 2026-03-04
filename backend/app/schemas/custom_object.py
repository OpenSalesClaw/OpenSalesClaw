"""Pydantic schemas for CustomObject and CustomObjectRecord."""

import re
from typing import Any

from pydantic import BaseModel, field_validator

from app.schemas.base import StandardReadFields

_API_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")


class CustomObjectCreate(BaseModel):
    api_name: str
    label: str
    plural_label: str
    description: str | None = None
    icon_name: str | None = None
    is_active: bool = True
    custom_fields: dict[str, Any] = {}

    @field_validator("api_name")
    @classmethod
    def validate_api_name(cls, v: str) -> str:
        if not _API_NAME_RE.match(v):
            raise ValueError("api_name must be lowercase letters, digits, and underscores, starting with a letter.")
        return v


class CustomObjectUpdate(BaseModel):
    label: str | None = None
    plural_label: str | None = None
    description: str | None = None
    icon_name: str | None = None
    is_active: bool | None = None
    custom_fields: dict[str, Any] | None = None


class CustomObjectRead(StandardReadFields):
    id: int
    api_name: str
    label: str
    plural_label: str
    description: str | None
    icon_name: str | None
    is_active: bool


# ---------------------------------------------------------------------------
# Records
# ---------------------------------------------------------------------------


class CustomObjectRecordCreate(BaseModel):
    name: str | None = None
    data: dict[str, Any] = {}
    custom_fields: dict[str, Any] = {}


class CustomObjectRecordUpdate(BaseModel):
    name: str | None = None
    data: dict[str, Any] | None = None
    custom_fields: dict[str, Any] | None = None


class CustomObjectRecordRead(StandardReadFields):
    id: int
    custom_object_id: int
    name: str | None
    data: dict[str, Any]

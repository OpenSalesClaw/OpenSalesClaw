from typing import Any

from pydantic import BaseModel

from app.schemas.base import StandardReadFields


class RoleCreate(BaseModel):
    name: str
    parent_role_id: int | None = None
    description: str | None = None
    custom_fields: dict[str, Any] = {}


class RoleUpdate(BaseModel):
    name: str | None = None
    parent_role_id: int | None = None
    description: str | None = None
    custom_fields: dict[str, Any] | None = None


class RoleRead(StandardReadFields):
    id: int
    name: str
    parent_role_id: int | None
    description: str | None

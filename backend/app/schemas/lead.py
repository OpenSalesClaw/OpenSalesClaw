from typing import Any

from pydantic import BaseModel, field_validator

from app.models.lead import LEAD_STATUSES
from app.schemas.base import StandardReadFields, TZAwareDatetime


class LeadCreate(BaseModel):
    last_name: str
    company: str
    first_name: str | None = None
    email: str | None = None
    phone: str | None = None
    title: str | None = None
    status: str = "New"
    lead_source: str | None = None
    industry: str | None = None
    custom_fields: dict[str, Any] = {}

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in LEAD_STATUSES:
            raise ValueError(f"status must be one of: {', '.join(LEAD_STATUSES)}")
        return v


class LeadUpdate(BaseModel):
    last_name: str | None = None
    company: str | None = None
    first_name: str | None = None
    email: str | None = None
    phone: str | None = None
    title: str | None = None
    status: str | None = None
    lead_source: str | None = None
    industry: str | None = None
    custom_fields: dict[str, Any] | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None and v not in LEAD_STATUSES:
            raise ValueError(f"status must be one of: {', '.join(LEAD_STATUSES)}")
        return v


class LeadRead(StandardReadFields):
    id: int
    first_name: str | None
    last_name: str
    email: str | None
    phone: str | None
    company: str
    title: str | None
    status: str
    lead_source: str | None
    industry: str | None
    converted_at: TZAwareDatetime | None
    converted_account_id: int | None
    converted_contact_id: int | None

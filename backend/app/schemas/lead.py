from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


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


class LeadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    converted_at: datetime | None
    converted_account_id: int | None
    converted_contact_id: int | None
    custom_fields: dict[str, Any]
    owner_id: int | None
    created_by_id: int | None
    updated_by_id: int | None
    created_at: datetime
    updated_at: datetime

from typing import Any

from pydantic import BaseModel, field_validator

from app.models.case import CASE_PRIORITIES, CASE_STATUSES
from app.schemas.base import StandardReadFields, TZAwareDatetime


class CaseCreate(BaseModel):
    subject: str
    account_id: int | None = None
    contact_id: int | None = None
    description: str | None = None
    status: str = "New"
    priority: str = "Medium"
    origin: str | None = None
    type: str | None = None
    reason: str | None = None
    custom_fields: dict[str, Any] = {}

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in CASE_STATUSES:
            raise ValueError(f"status must be one of: {', '.join(CASE_STATUSES)}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        if v not in CASE_PRIORITIES:
            raise ValueError(f"priority must be one of: {', '.join(CASE_PRIORITIES)}")
        return v


class CaseUpdate(BaseModel):
    subject: str | None = None
    account_id: int | None = None
    contact_id: int | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    origin: str | None = None
    type: str | None = None
    reason: str | None = None
    custom_fields: dict[str, Any] | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None and v not in CASE_STATUSES:
            raise ValueError(f"status must be one of: {', '.join(CASE_STATUSES)}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str | None) -> str | None:
        if v is not None and v not in CASE_PRIORITIES:
            raise ValueError(f"priority must be one of: {', '.join(CASE_PRIORITIES)}")
        return v


class CaseRead(StandardReadFields):
    id: int
    case_number: str | None
    subject: str
    account_id: int | None
    contact_id: int | None
    description: str | None
    status: str
    priority: str
    origin: str | None
    type: str | None
    reason: str | None
    closed_at: TZAwareDatetime | None

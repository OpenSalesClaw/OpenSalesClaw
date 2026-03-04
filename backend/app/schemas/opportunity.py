from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, field_validator

from app.models.opportunity import OPPORTUNITY_STAGES
from app.schemas.base import StandardReadFields


class OpportunityCreate(BaseModel):
    name: str
    account_id: int | None = None
    contact_id: int | None = None
    stage: str = "Prospecting"
    probability: int | None = None
    amount: Decimal | None = None
    close_date: date
    type: str | None = None
    lead_source: str | None = None
    next_step: str | None = None
    description: str | None = None
    custom_fields: dict[str, Any] = {}

    @field_validator("probability")
    @classmethod
    def validate_probability(cls, v: int | None) -> int | None:
        if v is not None and not (0 <= v <= 100):
            raise ValueError("probability must be between 0 and 100")
        return v

    @field_validator("stage")
    @classmethod
    def validate_stage(cls, v: str) -> str:
        if v not in OPPORTUNITY_STAGES:
            raise ValueError(f"stage must be one of: {', '.join(OPPORTUNITY_STAGES)}")
        return v


class OpportunityUpdate(BaseModel):
    name: str | None = None
    account_id: int | None = None
    contact_id: int | None = None
    stage: str | None = None
    probability: int | None = None
    amount: Decimal | None = None
    close_date: date | None = None
    type: str | None = None
    lead_source: str | None = None
    next_step: str | None = None
    description: str | None = None
    custom_fields: dict[str, Any] | None = None

    @field_validator("probability")
    @classmethod
    def validate_probability(cls, v: int | None) -> int | None:
        if v is not None and not (0 <= v <= 100):
            raise ValueError("probability must be between 0 and 100")
        return v

    @field_validator("stage")
    @classmethod
    def validate_stage(cls, v: str | None) -> str | None:
        if v is not None and v not in OPPORTUNITY_STAGES:
            raise ValueError(f"stage must be one of: {', '.join(OPPORTUNITY_STAGES)}")
        return v


class OpportunityRead(StandardReadFields):
    id: int
    name: str
    account_id: int | None
    contact_id: int | None
    stage: str
    probability: int | None
    amount: Decimal | None
    close_date: date
    type: str | None
    lead_source: str | None
    next_step: str | None
    description: str | None
    is_won: bool
    is_closed: bool

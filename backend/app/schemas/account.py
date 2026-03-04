from decimal import Decimal
from typing import Any

from pydantic import BaseModel

from app.schemas.base import StandardReadFields


class AccountCreate(BaseModel):
    name: str
    type: str | None = None
    industry: str | None = None
    website: str | None = None
    phone: str | None = None
    billing_street: str | None = None
    billing_city: str | None = None
    billing_state: str | None = None
    billing_postal_code: str | None = None
    billing_country: str | None = None
    description: str | None = None
    annual_revenue: Decimal | None = None
    number_of_employees: int | None = None
    custom_fields: dict[str, Any] = {}


class AccountUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    industry: str | None = None
    website: str | None = None
    phone: str | None = None
    billing_street: str | None = None
    billing_city: str | None = None
    billing_state: str | None = None
    billing_postal_code: str | None = None
    billing_country: str | None = None
    description: str | None = None
    annual_revenue: Decimal | None = None
    number_of_employees: int | None = None
    custom_fields: dict[str, Any] | None = None


class AccountRead(StandardReadFields):
    id: int
    name: str
    type: str | None
    industry: str | None
    website: str | None
    phone: str | None
    billing_street: str | None
    billing_city: str | None
    billing_state: str | None
    billing_postal_code: str | None
    billing_country: str | None
    description: str | None
    annual_revenue: Decimal | None
    number_of_employees: int | None

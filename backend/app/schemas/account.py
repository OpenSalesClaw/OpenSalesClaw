from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


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
    custom_fields: dict = {}


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
    custom_fields: dict | None = None


class AccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    custom_fields: dict
    owner_id: int | None
    created_by_id: int | None
    updated_by_id: int | None
    created_at: datetime
    updated_at: datetime

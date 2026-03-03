from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ContactCreate(BaseModel):
    last_name: str
    first_name: str | None = None
    account_id: int | None = None
    email: str | None = None
    phone: str | None = None
    mobile_phone: str | None = None
    title: str | None = None
    department: str | None = None
    mailing_street: str | None = None
    mailing_city: str | None = None
    mailing_state: str | None = None
    mailing_postal_code: str | None = None
    mailing_country: str | None = None
    custom_fields: dict = {}


class ContactUpdate(BaseModel):
    last_name: str | None = None
    first_name: str | None = None
    account_id: int | None = None
    email: str | None = None
    phone: str | None = None
    mobile_phone: str | None = None
    title: str | None = None
    department: str | None = None
    mailing_street: str | None = None
    mailing_city: str | None = None
    mailing_state: str | None = None
    mailing_postal_code: str | None = None
    mailing_country: str | None = None
    custom_fields: dict | None = None


class ContactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str | None
    last_name: str
    account_id: int | None
    email: str | None
    phone: str | None
    mobile_phone: str | None
    title: str | None
    department: str | None
    mailing_street: str | None
    mailing_city: str | None
    mailing_state: str | None
    mailing_postal_code: str | None
    mailing_country: str | None
    custom_fields: dict
    owner_id: int | None
    created_by_id: int | None
    updated_by_id: int | None
    created_at: datetime
    updated_at: datetime

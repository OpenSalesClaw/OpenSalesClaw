from typing import Any

from pydantic import BaseModel

from app.schemas.base import StandardReadFields


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
    custom_fields: dict[str, Any] = {}


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
    custom_fields: dict[str, Any] | None = None


class ContactRead(StandardReadFields):
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

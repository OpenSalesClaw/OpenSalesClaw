"""Pydantic schemas for CustomFieldDefinition."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, model_validator

from app.schemas.base import StandardReadFields


class FieldType(str, Enum):
    text = "text"
    number = "number"
    date = "date"
    datetime = "datetime"
    boolean = "boolean"
    picklist = "picklist"
    email = "email"
    url = "url"
    phone = "phone"
    currency = "currency"
    percent = "percent"
    textarea = "textarea"


class CustomFieldDefinitionCreate(BaseModel):
    object_name: str
    field_name: str
    field_label: str | None = None
    field_type: FieldType
    is_required: bool = False
    default_value: str | None = None
    picklist_values: list[str] | None = None
    field_order: int | None = None
    description: str | None = None
    custom_fields: dict[str, Any] = {}

    @model_validator(mode="after")
    def validate_picklist_values(self) -> "CustomFieldDefinitionCreate":
        if self.field_type == FieldType.picklist:
            if not self.picklist_values or len(self.picklist_values) == 0:
                raise ValueError("picklist_values must be a non-empty list when field_type is 'picklist'")
        return self


class CustomFieldDefinitionUpdate(BaseModel):
    field_label: str | None = None
    is_required: bool | None = None
    default_value: str | None = None
    picklist_values: list[str] | None = None
    field_order: int | None = None
    description: str | None = None
    custom_fields: dict[str, Any] | None = None


class CustomFieldDefinitionRead(StandardReadFields):
    id: int
    object_name: str
    field_name: str
    field_label: str | None
    field_type: str
    is_required: bool
    default_value: str | None
    picklist_values: list[str] | None
    field_order: int | None
    description: str | None

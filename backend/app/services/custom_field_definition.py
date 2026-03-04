"""Business logic for CustomFieldDefinition and custom field validation."""

import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError
from app.models.custom_field_definition import CustomFieldDefinition
from app.schemas.custom_field_definition import (
    CustomFieldDefinitionCreate,
    CustomFieldDefinitionUpdate,
    FieldType,
)
from app.services.base import CRUDService

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_URL_RE = re.compile(r"^https?://", re.IGNORECASE)


class CustomFieldDefinitionService(
    CRUDService[CustomFieldDefinition, CustomFieldDefinitionCreate, CustomFieldDefinitionUpdate]
):
    model = CustomFieldDefinition

    def apply_list_filters(self, query: Any, **filters: Any) -> Any:
        if object_name := filters.get("object_name"):
            query = query.where(CustomFieldDefinition.object_name == object_name)
        return query

    async def get_definitions_for_object(self, db: AsyncSession, object_name: str) -> list[CustomFieldDefinition]:
        result = await db.execute(
            select(CustomFieldDefinition)
            .where(
                CustomFieldDefinition.object_name == object_name,
                CustomFieldDefinition.is_deleted.is_(False),
            )
            .order_by(CustomFieldDefinition.field_order.nulls_last(), CustomFieldDefinition.id)
        )
        return list(result.scalars().all())

    async def validate_custom_fields(self, db: AsyncSession, object_name: str, custom_fields: dict[str, Any]) -> None:
        """Validate custom_fields dict against definitions for the given object.

        Raises ValidationError if:
        - Unknown field names are present
        - A value has the wrong type
        - A required field is missing
        - A picklist value is not in the allowed list
        """
        definitions = await self.get_definitions_for_object(db, object_name)
        if not definitions:
            return  # No definitions configured — accept any custom fields

        definition_map = {d.field_name: d for d in definitions}

        # Check for unknown fields
        for field_name in custom_fields:
            if field_name not in definition_map:
                raise ValidationError(f"Unknown custom field '{field_name}' for object '{object_name}'.")

        # Validate each defined field
        for definition in definitions:
            field_name = definition.field_name
            value = custom_fields.get(field_name)

            # Check required
            if definition.is_required and (value is None or value == ""):
                raise ValidationError(f"Custom field '{field_name}' is required.")

            if value is None:
                continue

            ft = definition.field_type
            try:
                field_type = FieldType(ft)
            except ValueError:
                continue  # Unknown field type — skip type validation

            match field_type:
                case FieldType.text | FieldType.textarea | FieldType.phone:
                    if not isinstance(value, str):
                        raise ValidationError(f"Custom field '{field_name}' must be a string.")
                case FieldType.number | FieldType.currency | FieldType.percent:
                    if not isinstance(value, (int, float)):
                        raise ValidationError(f"Custom field '{field_name}' must be a number.")
                case FieldType.boolean:
                    if not isinstance(value, bool):
                        raise ValidationError(f"Custom field '{field_name}' must be a boolean.")
                case FieldType.date:
                    if not isinstance(value, str):
                        raise ValidationError(f"Custom field '{field_name}' must be a date string (YYYY-MM-DD).")
                    try:
                        from datetime import date

                        date.fromisoformat(value)
                    except ValueError:
                        raise ValidationError(f"Custom field '{field_name}' must be a valid date string (YYYY-MM-DD).")
                case FieldType.datetime:
                    if not isinstance(value, str):
                        raise ValidationError(f"Custom field '{field_name}' must be a datetime string.")
                case FieldType.email:
                    if not isinstance(value, str) or not _EMAIL_RE.match(value):
                        raise ValidationError(f"Custom field '{field_name}' must be a valid email address.")
                case FieldType.url:
                    if not isinstance(value, str) or not _URL_RE.match(value):
                        raise ValidationError(f"Custom field '{field_name}' must be a valid URL (http/https).")
                case FieldType.picklist:
                    allowed = list(definition.picklist_values or [])
                    if value not in allowed:
                        raise ValidationError(
                            f"Custom field '{field_name}' value '{value}' is not in the allowed list: {allowed}."
                        )


custom_field_definition_service = CustomFieldDefinitionService()

get_custom_field_definition_by_id = custom_field_definition_service.get_by_id
list_custom_field_definitions = custom_field_definition_service.list
create_custom_field_definition = custom_field_definition_service.create
update_custom_field_definition = custom_field_definition_service.update
delete_custom_field_definition = custom_field_definition_service.delete
validate_custom_fields = custom_field_definition_service.validate_custom_fields

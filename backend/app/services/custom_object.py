"""Business logic for CustomObject and CustomObjectRecord."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.core.pagination import PaginationParams
from app.models.custom_object import CustomObject, CustomObjectRecord
from app.schemas.custom_object import (
    CustomObjectCreate,
    CustomObjectRecordCreate,
    CustomObjectRecordUpdate,
    CustomObjectUpdate,
)
from app.services.base import CRUDService


class CustomObjectService(CRUDService[CustomObject, CustomObjectCreate, CustomObjectUpdate]):
    model = CustomObject

    def apply_list_filters(self, query: Any, **filters: Any) -> Any:
        if (is_active := filters.get("is_active")) is not None:
            query = query.where(CustomObject.is_active == is_active)
        if label := filters.get("label"):
            from app.services.base import escape_like

            query = query.where(CustomObject.label.ilike(f"%{escape_like(label)}%"))
        return query

    async def get_by_api_name(self, db: AsyncSession, api_name: str) -> CustomObject:
        result = await db.execute(
            select(CustomObject).where(
                CustomObject.api_name == api_name,
                CustomObject.is_deleted.is_(False),
            )
        )
        obj = result.scalars().first()
        if obj is None:
            raise NotFoundError(f"CustomObject '{api_name}' not found.")
        return obj


class CustomObjectRecordService(CRUDService[CustomObjectRecord, CustomObjectRecordCreate, CustomObjectRecordUpdate]):
    model = CustomObjectRecord

    def apply_list_filters(self, query: Any, **filters: Any) -> Any:
        if custom_object_id := filters.get("custom_object_id"):
            query = query.where(CustomObjectRecord.custom_object_id == custom_object_id)
        if name := filters.get("name"):
            from app.services.base import escape_like

            query = query.where(CustomObjectRecord.name.ilike(f"%{escape_like(name)}%"))
        return query

    async def create_for_object(
        self,
        db: AsyncSession,
        custom_object_id: int,
        data: CustomObjectRecordCreate,
        created_by_id: int | None = None,
    ) -> CustomObjectRecord:
        """Create a record for the given custom object, validating data fields."""
        await self._validate_record_data(db, custom_object_id, data.data)
        record = CustomObjectRecord(
            custom_object_id=custom_object_id,
            name=data.name,
            data=data.data,
            custom_fields=data.custom_fields,
            created_by_id=created_by_id,
            updated_by_id=created_by_id,
            owner_id=created_by_id,
        )
        db.add(record)
        try:
            await db.flush()
        except Exception as exc:
            await db.rollback()
            raise ConflictError("A record with these values already exists.") from exc
        await db.refresh(record)
        return record

    async def update_record(
        self,
        db: AsyncSession,
        record_id: int,
        custom_object_id: int,
        data: CustomObjectRecordUpdate,
        updated_by_id: int | None = None,
    ) -> CustomObjectRecord:
        """Update a record, validating data fields if provided."""
        record = await self.get_by_id(db, record_id)
        updates = data.model_dump(exclude_unset=True)
        if "data" in updates and updates["data"] is not None:
            await self._validate_record_data(db, custom_object_id, updates["data"])
        for field, value in updates.items():
            setattr(record, field, value)
        record.updated_by_id = updated_by_id
        record.updated_at = datetime.now(UTC)
        await db.flush()
        await db.refresh(record)
        return record

    async def list_for_object(
        self,
        db: AsyncSession,
        custom_object_id: int,
        pagination: PaginationParams,
        name: str | None = None,
    ) -> tuple[list[CustomObjectRecord], int]:
        return await self.list(db, pagination, custom_object_id=custom_object_id, name=name)

    async def _validate_record_data(self, db: AsyncSession, custom_object_id: int, data: dict[str, Any]) -> None:
        """Validate data fields against CustomFieldDefinitions for this custom object.

        Uses the naming convention ``custom_object_{id}`` as the object_name.
        """
        from app.services.custom_field_definition import custom_field_definition_service

        object_name = f"custom_object_{custom_object_id}"
        await custom_field_definition_service.validate_custom_fields(db, object_name, data)


custom_object_service = CustomObjectService()
custom_object_record_service = CustomObjectRecordService()

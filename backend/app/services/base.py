"""Generic CRUD service base for standard entity operations."""

from datetime import UTC, datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.pagination import PaginationParams
from app.models.base import BaseEntity

ModelType = TypeVar("ModelType", bound=BaseEntity)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Reusable async CRUD operations for any entity model.

    Subclasses only need to set ``model`` and optionally override
    ``apply_list_filters`` for entity-specific query parameters.
    """

    model: type[ModelType]

    async def get_by_id(self, db: AsyncSession, record_id: int) -> ModelType:
        result = await db.execute(
            select(self.model).where(
                self.model.id == record_id,
                self.model.is_deleted.is_(False),
            )
        )
        record = result.scalars().first()
        if record is None:
            raise NotFoundError(f"{self.model.__name__} {record_id} not found.")
        return record

    async def list(
        self,
        db: AsyncSession,
        pagination: PaginationParams,
        *,
        order_by: Any | None = None,
        **filters: Any,
    ) -> tuple[list[ModelType], int]:
        query = select(self.model).where(self.model.is_deleted.is_(False))
        query = self.apply_list_filters(query, **filters)

        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar_one()

        if order_by is not None:
            query = query.order_by(order_by)
        else:
            query = query.order_by(self.model.created_at.desc())

        query = query.offset(pagination.offset).limit(pagination.limit)
        result = await db.execute(query)
        return list(result.scalars().all()), total

    def apply_list_filters(self, query: Any, **filters: Any) -> Any:
        """Override in subclasses to apply entity-specific filters."""
        return query

    async def create(self, db: AsyncSession, data: CreateSchemaType, created_by_id: int | None = None) -> ModelType:
        record = self.model(
            **data.model_dump(),
            created_by_id=created_by_id,
            updated_by_id=created_by_id,
            owner_id=created_by_id,
        )
        db.add(record)
        await db.flush()
        await db.refresh(record)
        return record

    async def update(
        self, db: AsyncSession, record_id: int, data: UpdateSchemaType, updated_by_id: int | None = None
    ) -> ModelType:
        record = await self.get_by_id(db, record_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(record, field, value)
        record.updated_by_id = updated_by_id
        await db.flush()
        await db.refresh(record)
        return record

    async def delete(self, db: AsyncSession, record_id: int, deleted_by_id: int | None = None) -> None:
        record = await self.get_by_id(db, record_id)
        record.is_deleted = True
        record.deleted_at = datetime.now(UTC)
        record.deleted_by_id = deleted_by_id
        await db.flush()

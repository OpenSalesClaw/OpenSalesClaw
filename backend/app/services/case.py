"""Business logic for the Case entity."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case, case_number_seq
from app.schemas.case import CaseCreate, CaseUpdate
from app.services.base import CRUDService

_CLOSED_STATUS = "Closed"


async def _generate_case_number(db: AsyncSession) -> str:
    """Generate the next sequential case number using a PostgreSQL sequence.

    Using a sequence instead of MAX()+1 eliminates the race condition where
    two concurrent requests could read the same max value and produce duplicate
    case numbers (which would then collide on the UNIQUE constraint → 500).
    """
    result = await db.execute(select(case_number_seq.next_value()))
    seq = result.scalar_one()
    return f"CS-{seq:05d}"


class CaseService(CRUDService[Case, CaseCreate, CaseUpdate]):
    model = Case

    def apply_list_filters(self, query: Any, **filters: Any) -> Any:
        if account_id := filters.get("account_id"):
            query = query.where(Case.account_id == account_id)
        if contact_id := filters.get("contact_id"):
            query = query.where(Case.contact_id == contact_id)
        if status := filters.get("status"):
            query = query.where(Case.status == status)
        if priority := filters.get("priority"):
            query = query.where(Case.priority == priority)
        return query

    async def list(
        self,
        db: AsyncSession,
        pagination: Any,
        *,
        order_by: Any | None = None,
        **filters: Any,
    ) -> tuple[list[Case], int]:
        # Default sort: created_at DESC; respect caller-supplied order_by.
        order_by = order_by if order_by is not None else self.model.created_at.desc()
        return await super().list(db, pagination, order_by=order_by, **filters)

    async def create(self, db: AsyncSession, data: CaseCreate, created_by_id: int | None = None) -> Case:
        payload = data.model_dump()

        await self._validate_custom_fields(db, payload)

        case_number = await _generate_case_number(db)
        closed_at = datetime.now(UTC) if payload["status"] == _CLOSED_STATUS else None

        record = Case(
            **payload,
            case_number=case_number,
            closed_at=closed_at,
            created_by_id=created_by_id,
            updated_by_id=created_by_id,
            owner_id=created_by_id,
        )
        db.add(record)
        await db.flush()
        await db.refresh(record)
        return record

    async def update(
        self, db: AsyncSession, record_id: int, data: CaseUpdate, updated_by_id: int | None = None
    ) -> Case:
        record = await self.get_by_id(db, record_id)
        updates = data.model_dump(exclude_unset=True)

        if "custom_fields" in updates and updates["custom_fields"] is not None:
            await self._validate_custom_fields(db, {"custom_fields": updates["custom_fields"]})

        if "status" in updates:
            if updates["status"] == _CLOSED_STATUS and not record.closed_at:
                updates["closed_at"] = datetime.now(UTC)
            elif updates["status"] != _CLOSED_STATUS:
                updates["closed_at"] = None

        for field, value in updates.items():
            setattr(record, field, value)
        record.updated_by_id = updated_by_id
        await db.flush()
        await db.refresh(record)
        return record


case_service = CaseService()

"""Business logic for the Case entity."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.schemas.case import CaseCreate, CaseUpdate
from app.services.base import CRUDService

_CLOSED_STATUS = "Closed"


async def _generate_case_number(db: AsyncSession) -> str:
    """Generate the next sequential case number in CS-NNNNN format."""
    result = await db.execute(
        select(func.max(Case.case_number)).where(Case.case_number.is_not(None))
    )
    max_number = result.scalar_one_or_none()
    if max_number:
        try:
            seq = int(max_number.split("-")[1]) + 1
        except (IndexError, ValueError):
            seq = 1
    else:
        seq = 1
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
        # Default sort: created_at DESC
        return await super().list(db, pagination, order_by=self.model.created_at.desc(), **filters)

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

get_case_by_id = case_service.get_by_id
list_cases = case_service.list
create_case = case_service.create
update_case = case_service.update
delete_case = case_service.delete

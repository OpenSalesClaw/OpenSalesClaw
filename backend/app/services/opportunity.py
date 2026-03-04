"""Business logic for the Opportunity entity."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.opportunity import DEFAULT_STAGE_PROBABILITIES, Opportunity
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate
from app.services.base import CRUDService

_CLOSED_WON = "Closed Won"
_CLOSED_LOST = "Closed Lost"


def _derive_closed_fields(stage: str) -> dict[str, Any]:
    """Return is_won, is_closed, and closed_at values derived from stage."""
    if stage == _CLOSED_WON:
        return {"is_won": True, "is_closed": True, "closed_at": datetime.now(UTC)}
    if stage == _CLOSED_LOST:
        return {"is_won": False, "is_closed": True, "closed_at": datetime.now(UTC)}
    return {"is_won": False, "is_closed": False, "closed_at": None}


class OpportunityService(CRUDService[Opportunity, OpportunityCreate, OpportunityUpdate]):
    model = Opportunity

    def apply_list_filters(self, query: Any, **filters: Any) -> Any:
        if account_id := filters.get("account_id"):
            query = query.where(Opportunity.account_id == account_id)
        if stage := filters.get("stage"):
            query = query.where(Opportunity.stage == stage)
        if filters.get("is_closed") is not None:
            query = query.where(Opportunity.is_closed.is_(filters["is_closed"]))
        if close_date_from := filters.get("close_date_from"):
            query = query.where(Opportunity.close_date >= close_date_from)
        if close_date_to := filters.get("close_date_to"):
            query = query.where(Opportunity.close_date <= close_date_to)
        return query

    async def create(
        self, db: AsyncSession, data: OpportunityCreate, created_by_id: int | None = None
    ) -> Opportunity:
        payload = data.model_dump()

        # Auto-set probability from stage defaults if not provided
        if payload.get("probability") is None:
            payload["probability"] = DEFAULT_STAGE_PROBABILITIES.get(payload["stage"], 10)

        # Derive closed fields from stage
        payload.update(_derive_closed_fields(payload["stage"]))

        await self._validate_custom_fields(db, payload)

        record = Opportunity(
            **payload,
            created_by_id=created_by_id,
            updated_by_id=created_by_id,
            owner_id=created_by_id,
        )
        db.add(record)
        await db.flush()
        await db.refresh(record)
        return record

    async def update(
        self, db: AsyncSession, record_id: int, data: OpportunityUpdate, updated_by_id: int | None = None
    ) -> Opportunity:
        record = await self.get_by_id(db, record_id)
        updates = data.model_dump(exclude_unset=True)

        if "stage" in updates:
            updates.update(_derive_closed_fields(updates["stage"]))
            # Auto-set probability when stage changes and probability not explicitly provided
            if "probability" not in data.model_fields_set:
                updates["probability"] = DEFAULT_STAGE_PROBABILITIES.get(updates["stage"], 10)

        for field, value in updates.items():
            setattr(record, field, value)
        record.updated_by_id = updated_by_id
        await db.flush()
        await db.refresh(record)
        return record

    async def get_pipeline(self, db: AsyncSession) -> list[dict[str, Any]]:
        """Return counts and sum of amounts grouped by stage."""
        from sqlalchemy import func

        result = await db.execute(
            select(
                Opportunity.stage,
                func.count(Opportunity.id).label("count"),
                func.coalesce(func.sum(Opportunity.amount), 0).label("total_amount"),
            )
            .where(Opportunity.is_deleted.is_(False), Opportunity.is_closed.is_(False))
            .group_by(Opportunity.stage)
        )
        rows = result.all()
        return [
            {"stage": row.stage, "count": row.count, "total_amount": float(row.total_amount)}
            for row in rows
        ]


opportunity_service = OpportunityService()

get_opportunity_by_id = opportunity_service.get_by_id
list_opportunities = opportunity_service.list
create_opportunity = opportunity_service.create
update_opportunity = opportunity_service.update
delete_opportunity = opportunity_service.delete
get_pipeline = opportunity_service.get_pipeline

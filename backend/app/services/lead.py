from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.pagination import PaginationParams
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadUpdate


async def get_lead_by_id(db: AsyncSession, lead_id: int) -> Lead:
    result = await db.execute(select(Lead).where(Lead.id == lead_id, Lead.is_deleted.is_(False)))
    lead = result.scalars().first()
    if lead is None:
        raise NotFoundError(f"Lead {lead_id} not found.")
    return lead


async def list_leads(
    db: AsyncSession,
    pagination: PaginationParams,
    status: str | None = None,
    company: str | None = None,
    email: str | None = None,
) -> tuple[list[Lead], int]:
    query = select(Lead).where(Lead.is_deleted.is_(False))
    if status:
        query = query.where(Lead.status == status)
    if company:
        query = query.where(Lead.company.ilike(f"%{company}%"))
    if email:
        query = query.where(Lead.email.ilike(f"%{email}%"))

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    query = query.order_by(Lead.created_at.desc()).offset(pagination.offset).limit(pagination.limit)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def create_lead(db: AsyncSession, data: LeadCreate, created_by_id: int | None = None) -> Lead:
    lead = Lead(
        **data.model_dump(),
        created_by_id=created_by_id,
        updated_by_id=created_by_id,
        owner_id=created_by_id,
    )
    db.add(lead)
    await db.flush()
    await db.refresh(lead)
    return lead


async def update_lead(db: AsyncSession, lead_id: int, data: LeadUpdate, updated_by_id: int | None = None) -> Lead:
    lead = await get_lead_by_id(db, lead_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)
    lead.updated_by_id = updated_by_id
    await db.flush()
    await db.refresh(lead)
    return lead


async def delete_lead(db: AsyncSession, lead_id: int, deleted_by_id: int | None = None) -> None:
    lead = await get_lead_by_id(db, lead_id)
    lead.is_deleted = True
    lead.deleted_at = datetime.now(UTC)
    lead.deleted_by_id = deleted_by_id
    await db.flush()

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.user import User
from app.schemas.lead import LeadCreate, LeadRead, LeadUpdate
from app.services.lead import lead_service

router = APIRouter(prefix="/api/leads", tags=["leads"])


@router.get("", response_model=PaginatedResponse[LeadRead])
async def list_leads(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    pagination: Annotated[PaginationParams, Depends()],
    lead_status: str | None = Query(default=None, alias="status", description="Filter by status"),
    company: str | None = Query(default=None, description="Filter by company (partial match)"),
    email: str | None = Query(default=None, description="Filter by email (partial match)"),
    owner_id: int | None = Query(default=None, description="Filter by owner ID"),
) -> PaginatedResponse[LeadRead]:
    items, total = await lead_service.list(
        db, pagination, status=lead_status, company=company, email=email, owner_id=owner_id
    )
    return PaginatedResponse.from_result([LeadRead.model_validate(i) for i in items], total, pagination)


@router.get("/{lead_id}", response_model=LeadRead)
async def get_lead(
    lead_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> LeadRead:
    return LeadRead.model_validate(await lead_service.get_by_id(db, lead_id))


@router.post("", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
async def create_lead(
    data: LeadCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> LeadRead:
    return LeadRead.model_validate(await lead_service.create(db, data, created_by_id=current_user.id))


@router.patch("/{lead_id}", response_model=LeadRead)
async def update_lead(
    lead_id: int,
    data: LeadUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> LeadRead:
    return LeadRead.model_validate(await lead_service.update(db, lead_id, data, updated_by_id=current_user.id))


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> None:
    await lead_service.delete(db, lead_id, deleted_by_id=current_user.id)

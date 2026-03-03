from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.pagination import PaginatedResponse, PaginationParams
from app.schemas.lead import LeadCreate, LeadRead, LeadUpdate
from app.services import lead as lead_service

router = APIRouter(prefix="/api/leads", tags=["leads"])


@router.get("", response_model=PaginatedResponse[LeadRead])
async def list_leads(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_active_user)],
    pagination: Annotated[PaginationParams, Depends()],
    lead_status: str | None = Query(default=None, alias="status", description="Filter by status"),
    company: str | None = Query(default=None, description="Filter by company (partial match)"),
    email: str | None = Query(default=None, description="Filter by email (partial match)"),
) -> PaginatedResponse[LeadRead]:
    items, total = await lead_service.list_leads(db, pagination, status=lead_status, company=company, email=email)
    return PaginatedResponse(items=items, total=total, offset=pagination.offset, limit=pagination.limit)


@router.get("/{lead_id}", response_model=LeadRead)
async def get_lead(
    lead_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_active_user)],
) -> LeadRead:
    return await lead_service.get_lead_by_id(db, lead_id)


@router.post("", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
async def create_lead(
    data: LeadCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_active_user)],
) -> LeadRead:
    return await lead_service.create_lead(db, data, created_by_id=current_user["id"])


@router.patch("/{lead_id}", response_model=LeadRead)
async def update_lead(
    lead_id: int,
    data: LeadUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_active_user)],
) -> LeadRead:
    return await lead_service.update_lead(db, lead_id, data, updated_by_id=current_user["id"])


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_active_user)],
) -> None:
    await lead_service.delete_lead(db, lead_id, deleted_by_id=current_user["id"])

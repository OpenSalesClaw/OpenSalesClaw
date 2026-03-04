from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.user import User
from app.schemas.opportunity import OpportunityCreate, OpportunityRead, OpportunityUpdate
from app.services.opportunity import opportunity_service

router = APIRouter(prefix="/api/opportunities", tags=["opportunities"])


@router.get("", response_model=PaginatedResponse[OpportunityRead])
async def list_opportunities(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    pagination: Annotated[PaginationParams, Depends()],
    account_id: int | None = Query(default=None, description="Filter by account ID"),
    stage: str | None = Query(default=None, description="Filter by stage"),
    is_closed: bool | None = Query(default=None, description="Filter by closed status"),
    close_date_from: date | None = Query(default=None, description="Filter by close date (from)"),
    close_date_to: date | None = Query(default=None, description="Filter by close date (to)"),
    owner_id: int | None = Query(default=None, description="Filter by owner ID"),
) -> PaginatedResponse[OpportunityRead]:
    items, total = await opportunity_service.list(
        db,
        pagination,
        account_id=account_id,
        stage=stage,
        is_closed=is_closed,
        close_date_from=close_date_from,
        close_date_to=close_date_to,
        owner_id=owner_id,
    )
    return PaginatedResponse.from_result([OpportunityRead.model_validate(i) for i in items], total, pagination)


@router.get("/pipeline", response_model=list[dict[str, Any]])
async def get_pipeline(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> list[dict[str, Any]]:
    return await opportunity_service.get_pipeline(db)


@router.get("/{opportunity_id}", response_model=OpportunityRead)
async def get_opportunity(
    opportunity_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> OpportunityRead:
    return OpportunityRead.model_validate(await opportunity_service.get_by_id(db, opportunity_id))


@router.post("", response_model=OpportunityRead, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    data: OpportunityCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> OpportunityRead:
    return OpportunityRead.model_validate(await opportunity_service.create(db, data, created_by_id=current_user.id))


@router.patch("/{opportunity_id}", response_model=OpportunityRead)
async def update_opportunity(
    opportunity_id: int,
    data: OpportunityUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> OpportunityRead:
    return OpportunityRead.model_validate(
        await opportunity_service.update(db, opportunity_id, data, updated_by_id=current_user.id)
    )


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_opportunity(
    opportunity_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> None:
    await opportunity_service.delete(db, opportunity_id, deleted_by_id=current_user.id)

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.user import User
from app.schemas.case import CaseCreate, CaseRead, CaseUpdate
from app.services.case import case_service

router = APIRouter(prefix="/api/cases", tags=["cases"])


@router.get("", response_model=PaginatedResponse[CaseRead])
async def list_cases(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    pagination: Annotated[PaginationParams, Depends()],
    account_id: int | None = Query(default=None, description="Filter by account ID"),
    contact_id: int | None = Query(default=None, description="Filter by contact ID"),
    status: str | None = Query(default=None, description="Filter by status"),
    priority: str | None = Query(default=None, description="Filter by priority"),
    owner_id: int | None = Query(default=None, description="Filter by owner ID"),
) -> PaginatedResponse[CaseRead]:
    items, total = await case_service.list(
        db,
        pagination,
        account_id=account_id,
        contact_id=contact_id,
        status=status,
        priority=priority,
        owner_id=owner_id,
    )
    return PaginatedResponse.from_result([CaseRead.model_validate(i) for i in items], total, pagination)


@router.get("/{case_id}", response_model=CaseRead)
async def get_case(
    case_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> CaseRead:
    return CaseRead.model_validate(await case_service.get_by_id(db, case_id))


@router.post("", response_model=CaseRead, status_code=status.HTTP_201_CREATED)
async def create_case(
    data: CaseCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> CaseRead:
    return CaseRead.model_validate(await case_service.create(db, data, created_by_id=current_user.id))


@router.patch("/{case_id}", response_model=CaseRead)
async def update_case(
    case_id: int,
    data: CaseUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> CaseRead:
    return CaseRead.model_validate(await case_service.update(db, case_id, data, updated_by_id=current_user.id))


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(
    case_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> None:
    await case_service.delete(db, case_id, deleted_by_id=current_user.id)

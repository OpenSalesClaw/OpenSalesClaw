from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.user import User
from app.schemas.account import AccountCreate, AccountRead, AccountUpdate
from app.services import account as account_service

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.get("", response_model=PaginatedResponse[AccountRead])
async def list_accounts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    pagination: Annotated[PaginationParams, Depends()],
    name: str | None = Query(default=None, description="Filter by name (partial match)"),
    type: str | None = Query(default=None, description="Filter by account type"),
    industry: str | None = Query(default=None, description="Filter by industry (partial match)"),
) -> PaginatedResponse[AccountRead]:
    items, total = await account_service.list_accounts(db, pagination, name=name, type=type, industry=industry)
    return PaginatedResponse(items=items, total=total, offset=pagination.offset, limit=pagination.limit)  # type: ignore[arg-type]


@router.get("/{account_id}", response_model=AccountRead)
async def get_account(
    account_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> AccountRead:
    return await account_service.get_account_by_id(db, account_id)  # type: ignore[return-value]


@router.post("", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
async def create_account(
    data: AccountCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> AccountRead:
    return await account_service.create_account(db, data, created_by_id=current_user.id)  # type: ignore[return-value]


@router.patch("/{account_id}", response_model=AccountRead)
async def update_account(
    account_id: int,
    data: AccountUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> AccountRead:
    return await account_service.update_account(db, account_id, data, updated_by_id=current_user.id)  # type: ignore[return-value]


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> None:
    await account_service.delete_account(db, account_id, deleted_by_id=current_user.id)

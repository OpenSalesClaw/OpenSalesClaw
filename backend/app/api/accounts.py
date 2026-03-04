from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.user import User
from app.schemas.account import AccountCreate, AccountRead, AccountUpdate
from app.services.account import account_service

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.get("", response_model=PaginatedResponse[AccountRead])
async def list_accounts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    pagination: Annotated[PaginationParams, Depends()],
    name: str | None = Query(default=None, description="Filter by name (partial match)"),
    type: str | None = Query(default=None, description="Filter by account type"),
    industry: str | None = Query(default=None, description="Filter by industry (partial match)"),
    owner_id: int | None = Query(default=None, description="Filter by owner ID"),
) -> PaginatedResponse[AccountRead]:
    items, total = await account_service.list(
        db, pagination, name=name, type=type, industry=industry, owner_id=owner_id
    )
    return PaginatedResponse.from_result([AccountRead.model_validate(i) for i in items], total, pagination)


@router.get("/{account_id}", response_model=AccountRead)
async def get_account(
    account_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> AccountRead:
    return AccountRead.model_validate(await account_service.get_by_id(db, account_id))


@router.post("", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
async def create_account(
    data: AccountCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> AccountRead:
    return AccountRead.model_validate(await account_service.create(db, data, created_by_id=current_user.id))


@router.patch("/{account_id}", response_model=AccountRead)
async def update_account(
    account_id: int,
    data: AccountUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> AccountRead:
    return AccountRead.model_validate(await account_service.update(db, account_id, data, updated_by_id=current_user.id))


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> None:
    await account_service.delete(db, account_id, deleted_by_id=current_user.id)

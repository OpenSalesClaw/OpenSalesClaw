from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_superuser
from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.user import User
from app.schemas.user import UserList, UserRead, UserUpdate
from app.services import user as user_service

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=PaginatedResponse[UserList])
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
    pagination: Annotated[PaginationParams, Depends()],
    is_active: bool | None = Query(default=None, description="Filter by active status"),
    role_id: int | None = Query(default=None, description="Filter by role ID"),
    email: str | None = Query(default=None, description="Search by email (partial match)"),
) -> PaginatedResponse[UserList]:
    items, total = await user_service.list_users(
        db, pagination, is_active=is_active, role_id=role_id, email_search=email
    )
    return PaginatedResponse(items=items, total=total, offset=pagination.offset, limit=pagination.limit)  # type: ignore[arg-type]


@router.get("/me", response_model=UserRead)
async def get_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserRead:
    return current_user  # type: ignore[return-value]


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserRead:
    return await user_service.get_user_by_id(db, user_id)  # type: ignore[return-value]


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
) -> UserRead:
    return await user_service.update_user(db, user_id, data, updated_by_id=current_user.id)  # type: ignore[return-value]


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
) -> None:
    await user_service.deactivate_user(db, user_id, updated_by_id=current_user.id)

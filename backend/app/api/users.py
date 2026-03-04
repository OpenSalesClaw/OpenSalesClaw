from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_superuser
from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.user import User
from app.schemas.user import AdminUserCreate, PasswordReset, UserList, UserRead, UserUpdate
from app.services.user import user_service

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
    items, total = await user_service.list(db, pagination, is_active=is_active, role_id=role_id, email=email)
    return PaginatedResponse.from_result([UserList.model_validate(i) for i in items], total, pagination)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: AdminUserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
) -> UserRead:
    """Admin: create a new user with full control over is_active, is_superuser, and role."""
    return UserRead.model_validate(await user_service.create_admin_user(db, data, created_by_id=current_user.id))


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserRead:
    return UserRead.model_validate(await user_service.get_by_id(db, user_id))


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
) -> UserRead:
    if user_id == current_user.id:
        if data.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot deactivate your own account.",
            )
        if data.is_superuser is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot remove superuser from your own account.",
            )
    return UserRead.model_validate(await user_service.update(db, user_id, data, updated_by_id=current_user.id))


@router.patch("/{user_id}/reset-password", response_model=UserRead)
async def reset_user_password(
    user_id: int,
    data: PasswordReset,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
) -> UserRead:
    """Admin: reset any user's password without requiring the old password."""
    return UserRead.model_validate(
        await user_service.reset_password(db, user_id, data.new_password, updated_by_id=current_user.id)
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
) -> None:
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot delete your own account.")
    await user_service.delete(db, user_id, deleted_by_id=current_user.id)

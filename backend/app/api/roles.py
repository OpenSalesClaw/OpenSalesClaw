from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_superuser
from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.user import User
from app.schemas.role import RoleCreate, RoleRead, RoleUpdate
from app.services import role as role_service

router = APIRouter(prefix="/api/roles", tags=["roles"])


@router.get("", response_model=PaginatedResponse[RoleRead])
async def list_roles(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    pagination: Annotated[PaginationParams, Depends()],
) -> PaginatedResponse[RoleRead]:
    items, total = await role_service.list_roles(db, pagination)
    return PaginatedResponse(items=items, total=total, offset=pagination.offset, limit=pagination.limit)  # type: ignore[arg-type]


@router.get("/hierarchy", response_model=list[dict[str, Any]])
async def get_hierarchy(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> list[dict[str, Any]]:
    return await role_service.get_role_hierarchy(db)


@router.get("/{role_id}", response_model=RoleRead)
async def get_role(
    role_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> RoleRead:
    return await role_service.get_role_by_id(db, role_id)  # type: ignore[return-value]


@router.post("", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: RoleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
) -> RoleRead:
    return await role_service.create_role(db, data, created_by_id=current_user.id)  # type: ignore[return-value]


@router.patch("/{role_id}", response_model=RoleRead)
async def update_role(
    role_id: int,
    data: RoleUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
) -> RoleRead:
    return await role_service.update_role(db, role_id, data, updated_by_id=current_user.id)  # type: ignore[return-value]


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
) -> None:
    await role_service.delete_role(db, role_id, deleted_by_id=current_user.id)

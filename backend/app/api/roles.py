from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_superuser
from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.user import User
from app.schemas.role import RoleCreate, RoleRead, RoleUpdate
from app.services.role import role_service

router = APIRouter(prefix="/api/roles", tags=["roles"])


@router.get("", response_model=PaginatedResponse[RoleRead])
async def list_roles(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    pagination: Annotated[PaginationParams, Depends()],
) -> PaginatedResponse[RoleRead]:
    items, total = await role_service.list(db, pagination)
    return PaginatedResponse.from_result([RoleRead.model_validate(i) for i in items], total, pagination)


@router.get("/hierarchy", response_model=list[dict[str, Any]])
async def get_hierarchy(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> list[dict[str, Any]]:
    return await role_service.get_hierarchy(db)


@router.get("/{role_id}", response_model=RoleRead)
async def get_role(
    role_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> RoleRead:
    return RoleRead.model_validate(await role_service.get_by_id(db, role_id))


@router.post("", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: RoleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
) -> RoleRead:
    return RoleRead.model_validate(await role_service.create(db, data, created_by_id=current_user.id))


@router.patch("/{role_id}", response_model=RoleRead)
async def update_role(
    role_id: int,
    data: RoleUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
) -> RoleRead:
    return RoleRead.model_validate(await role_service.update(db, role_id, data, updated_by_id=current_user.id))


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
) -> None:
    await role_service.delete(db, role_id, deleted_by_id=current_user.id)

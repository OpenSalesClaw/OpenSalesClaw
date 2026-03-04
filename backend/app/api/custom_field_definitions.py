from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_superuser
from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.user import User
from app.schemas.custom_field_definition import (
    CustomFieldDefinitionCreate,
    CustomFieldDefinitionRead,
    CustomFieldDefinitionUpdate,
)
from app.services import custom_field_definition as cfd_service

router = APIRouter(prefix="/api/custom-field-definitions", tags=["custom-field-definitions"])


@router.get("", response_model=PaginatedResponse[CustomFieldDefinitionRead])
async def list_custom_field_definitions(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    pagination: Annotated[PaginationParams, Depends()],
    object_name: str | None = Query(default=None, description="Filter by object name (e.g. 'accounts')"),
) -> PaginatedResponse[CustomFieldDefinitionRead]:
    items, total = await cfd_service.list_custom_field_definitions(db, pagination, object_name=object_name)
    return PaginatedResponse(items=items, total=total, offset=pagination.offset, limit=pagination.limit)  # type: ignore[arg-type]


@router.get("/{definition_id}", response_model=CustomFieldDefinitionRead)
async def get_custom_field_definition(
    definition_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> CustomFieldDefinitionRead:
    return await cfd_service.get_custom_field_definition_by_id(db, definition_id)  # type: ignore[return-value]


@router.post("", response_model=CustomFieldDefinitionRead, status_code=status.HTTP_201_CREATED)
async def create_custom_field_definition(
    data: CustomFieldDefinitionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
) -> CustomFieldDefinitionRead:
    return await cfd_service.create_custom_field_definition(db, data, created_by_id=current_user.id)  # type: ignore[return-value]


@router.patch("/{definition_id}", response_model=CustomFieldDefinitionRead)
async def update_custom_field_definition(
    definition_id: int,
    data: CustomFieldDefinitionUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
) -> CustomFieldDefinitionRead:
    return await cfd_service.update_custom_field_definition(db, definition_id, data, updated_by_id=current_user.id)  # type: ignore[return-value]


@router.delete("/{definition_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_custom_field_definition(
    definition_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
) -> None:
    await cfd_service.delete_custom_field_definition(db, definition_id, deleted_by_id=current_user.id)

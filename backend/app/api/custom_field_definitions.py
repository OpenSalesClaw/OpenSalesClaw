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
from app.services.custom_field_definition import custom_field_definition_service

router = APIRouter(prefix="/api/custom-field-definitions", tags=["custom-field-definitions"])


@router.get("", response_model=PaginatedResponse[CustomFieldDefinitionRead])
async def list_custom_field_definitions(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    pagination: Annotated[PaginationParams, Depends()],
    object_name: str | None = Query(default=None, description="Filter by object name (e.g. 'accounts')"),
) -> PaginatedResponse[CustomFieldDefinitionRead]:
    items, total = await custom_field_definition_service.list(db, pagination, object_name=object_name)
    return PaginatedResponse.from_result(
        [CustomFieldDefinitionRead.model_validate(i) for i in items], total, pagination
    )


@router.get("/{definition_id}", response_model=CustomFieldDefinitionRead)
async def get_custom_field_definition(
    definition_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> CustomFieldDefinitionRead:
    return CustomFieldDefinitionRead.model_validate(await custom_field_definition_service.get_by_id(db, definition_id))


@router.post("", response_model=CustomFieldDefinitionRead, status_code=status.HTTP_201_CREATED)
async def create_custom_field_definition(
    data: CustomFieldDefinitionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
) -> CustomFieldDefinitionRead:
    return CustomFieldDefinitionRead.model_validate(
        await custom_field_definition_service.create(db, data, created_by_id=current_user.id)
    )


@router.patch("/{definition_id}", response_model=CustomFieldDefinitionRead)
async def update_custom_field_definition(
    definition_id: int,
    data: CustomFieldDefinitionUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
) -> CustomFieldDefinitionRead:
    return CustomFieldDefinitionRead.model_validate(
        await custom_field_definition_service.update(db, definition_id, data, updated_by_id=current_user.id)
    )


@router.delete("/{definition_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_custom_field_definition(
    definition_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
) -> None:
    await custom_field_definition_service.delete(db, definition_id, deleted_by_id=current_user.id)

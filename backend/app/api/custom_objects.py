"""API routes for Custom Objects and their records."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_superuser
from app.core.exceptions import NotFoundError
from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.user import User
from app.schemas.custom_object import (
    CustomObjectCreate,
    CustomObjectRead,
    CustomObjectRecordCreate,
    CustomObjectRecordRead,
    CustomObjectRecordUpdate,
    CustomObjectUpdate,
)
from app.services.custom_object import custom_object_record_service, custom_object_service

router = APIRouter(prefix="/api/custom-objects", tags=["custom-objects"])


# ─────────────────────────────────────────────────────────────────────────────
# Custom Object Definitions
# ─────────────────────────────────────────────────────────────────────────────


@router.get("", response_model=PaginatedResponse[CustomObjectRead])
async def list_custom_objects(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    pagination: Annotated[PaginationParams, Depends()],
    is_active: bool | None = Query(default=None, description="Filter by active status"),
    label: str | None = Query(default=None, description="Filter by label (partial match)"),
) -> PaginatedResponse[CustomObjectRead]:
    items, total = await custom_object_service.list(db, pagination, is_active=is_active, label=label)
    return PaginatedResponse.from_result([CustomObjectRead.model_validate(i) for i in items], total, pagination)


@router.post("", response_model=CustomObjectRead, status_code=status.HTTP_201_CREATED)
async def create_custom_object(
    data: CustomObjectCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
) -> CustomObjectRead:
    obj = await custom_object_service.create(db, data, created_by_id=current_user.id)
    return CustomObjectRead.model_validate(obj)


@router.get("/{api_name}", response_model=CustomObjectRead)
async def get_custom_object(
    api_name: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> CustomObjectRead:
    obj = await custom_object_service.get_by_api_name(db, api_name)
    return CustomObjectRead.model_validate(obj)


@router.patch("/{api_name}", response_model=CustomObjectRead)
async def update_custom_object(
    api_name: str,
    data: CustomObjectUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
) -> CustomObjectRead:
    obj = await custom_object_service.get_by_api_name(db, api_name)
    updated = await custom_object_service.update(db, obj.id, data, updated_by_id=current_user.id)
    return CustomObjectRead.model_validate(updated)


@router.delete("/{api_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_custom_object(
    api_name: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_superuser)],
) -> None:
    obj = await custom_object_service.get_by_api_name(db, api_name)
    await custom_object_service.delete(db, obj.id, deleted_by_id=current_user.id)


# ─────────────────────────────────────────────────────────────────────────────
# Custom Object Records
# ─────────────────────────────────────────────────────────────────────────────


@router.get("/{api_name}/records", response_model=PaginatedResponse[CustomObjectRecordRead])
async def list_records(
    api_name: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    pagination: Annotated[PaginationParams, Depends()],
    name: str | None = Query(default=None, description="Filter by record name (partial match)"),
) -> PaginatedResponse[CustomObjectRecordRead]:
    obj = await custom_object_service.get_by_api_name(db, api_name)
    items, total = await custom_object_record_service.list_for_object(db, obj.id, pagination, name=name)
    return PaginatedResponse.from_result([CustomObjectRecordRead.model_validate(i) for i in items], total, pagination)


@router.post("/{api_name}/records", response_model=CustomObjectRecordRead, status_code=status.HTTP_201_CREATED)
async def create_record(
    api_name: str,
    data: CustomObjectRecordCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> CustomObjectRecordRead:
    obj = await custom_object_service.get_by_api_name(db, api_name)
    record = await custom_object_record_service.create_for_object(db, obj.id, data, created_by_id=current_user.id)
    return CustomObjectRecordRead.model_validate(record)


@router.get("/{api_name}/records/{record_id}", response_model=CustomObjectRecordRead)
async def get_record(
    api_name: str,
    record_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> CustomObjectRecordRead:
    obj = await custom_object_service.get_by_api_name(db, api_name)
    record = await custom_object_record_service.get_by_id(db, record_id)
    if record.custom_object_id != obj.id:
        raise NotFoundError(f"Record {record_id} not found for object '{api_name}'.")
    return CustomObjectRecordRead.model_validate(record)


@router.patch("/{api_name}/records/{record_id}", response_model=CustomObjectRecordRead)
async def update_record(
    api_name: str,
    record_id: int,
    data: CustomObjectRecordUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> CustomObjectRecordRead:
    obj = await custom_object_service.get_by_api_name(db, api_name)
    record = await custom_object_record_service.get_by_id(db, record_id)
    if record.custom_object_id != obj.id:
        raise NotFoundError(f"Record {record_id} not found for object '{api_name}'.")
    updated = await custom_object_record_service.update_record(
        db, record_id, obj.id, data, updated_by_id=current_user.id
    )
    return CustomObjectRecordRead.model_validate(updated)


@router.delete("/{api_name}/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_record(
    api_name: str,
    record_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> None:
    obj = await custom_object_service.get_by_api_name(db, api_name)
    record = await custom_object_record_service.get_by_id(db, record_id)
    if record.custom_object_id != obj.id:
        raise NotFoundError(f"Record {record_id} not found for object '{api_name}'.")
    await custom_object_record_service.delete(db, record_id, deleted_by_id=current_user.id)

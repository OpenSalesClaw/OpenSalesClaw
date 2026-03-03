from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.pagination import PaginatedResponse, PaginationParams
from app.schemas.contact import ContactCreate, ContactRead, ContactUpdate
from app.services import contact as contact_service

router = APIRouter(prefix="/api/contacts", tags=["contacts"])


@router.get("", response_model=PaginatedResponse[ContactRead])
async def list_contacts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    pagination: Annotated[PaginationParams, Depends()],
    account_id: int | None = Query(default=None, description="Filter by account ID"),
    last_name: str | None = Query(default=None, description="Filter by last name (partial match)"),
    email: str | None = Query(default=None, description="Filter by email (partial match)"),
) -> PaginatedResponse[ContactRead]:
    items, total = await contact_service.list_contacts(
        db, pagination, account_id=account_id, last_name=last_name, email=email
    )
    return PaginatedResponse(items=items, total=total, offset=pagination.offset, limit=pagination.limit)  # type: ignore[arg-type]


@router.get("/{contact_id}", response_model=ContactRead)
async def get_contact(
    contact_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict[str, Any], Depends(get_current_active_user)],
) -> ContactRead:
    return await contact_service.get_contact_by_id(db, contact_id)  # type: ignore[return-value]


@router.post("", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
async def create_contact(
    data: ContactCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict[str, Any], Depends(get_current_active_user)],
) -> ContactRead:
    return await contact_service.create_contact(db, data, created_by_id=current_user["id"])  # type: ignore[return-value]


@router.patch("/{contact_id}", response_model=ContactRead)
async def update_contact(
    contact_id: int,
    data: ContactUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict[str, Any], Depends(get_current_active_user)],
) -> ContactRead:
    return await contact_service.update_contact(db, contact_id, data, updated_by_id=current_user["id"])  # type: ignore[return-value]


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict[str, Any], Depends(get_current_active_user)],
) -> None:
    await contact_service.delete_contact(db, contact_id, deleted_by_id=current_user["id"])

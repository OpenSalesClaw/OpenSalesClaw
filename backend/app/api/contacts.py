from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.user import User
from app.schemas.contact import ContactCreate, ContactRead, ContactUpdate
from app.services.contact import contact_service

router = APIRouter(prefix="/api/contacts", tags=["contacts"])


@router.get("", response_model=PaginatedResponse[ContactRead])
async def list_contacts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    pagination: Annotated[PaginationParams, Depends()],
    account_id: int | None = Query(default=None, description="Filter by account ID"),
    last_name: str | None = Query(default=None, description="Filter by last name (partial match)"),
    email: str | None = Query(default=None, description="Filter by email (partial match)"),
    owner_id: int | None = Query(default=None, description="Filter by owner ID"),
) -> PaginatedResponse[ContactRead]:
    items, total = await contact_service.list(
        db, pagination, account_id=account_id, last_name=last_name, email=email, owner_id=owner_id
    )
    return PaginatedResponse.from_result([ContactRead.model_validate(i) for i in items], total, pagination)


@router.get("/{contact_id}", response_model=ContactRead)
async def get_contact(
    contact_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ContactRead:
    return ContactRead.model_validate(await contact_service.get_by_id(db, contact_id))


@router.post("", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
async def create_contact(
    data: ContactCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ContactRead:
    return ContactRead.model_validate(await contact_service.create(db, data, created_by_id=current_user.id))


@router.patch("/{contact_id}", response_model=ContactRead)
async def update_contact(
    contact_id: int,
    data: ContactUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ContactRead:
    return ContactRead.model_validate(await contact_service.update(db, contact_id, data, updated_by_id=current_user.id))


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> None:
    await contact_service.delete(db, contact_id, deleted_by_id=current_user.id)

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.pagination import PaginationParams
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate


async def get_contact_by_id(db: AsyncSession, contact_id: int) -> Contact:
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.is_deleted.is_(False))
    )
    contact = result.scalars().first()
    if contact is None:
        raise NotFoundError(f"Contact {contact_id} not found.")
    return contact


async def list_contacts(
    db: AsyncSession,
    pagination: PaginationParams,
    account_id: int | None = None,
    last_name: str | None = None,
    email: str | None = None,
) -> tuple[list[Contact], int]:
    query = select(Contact).where(Contact.is_deleted.is_(False))
    if account_id is not None:
        query = query.where(Contact.account_id == account_id)
    if last_name:
        query = query.where(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.where(Contact.email.ilike(f"%{email}%"))

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    query = query.order_by(Contact.last_name.asc()).offset(pagination.offset).limit(pagination.limit)
    result = await db.execute(query)
    return result.scalars().all(), total


async def create_contact(db: AsyncSession, data: ContactCreate, created_by_id: int | None = None) -> Contact:
    contact = Contact(
        **data.model_dump(),
        created_by_id=created_by_id,
        updated_by_id=created_by_id,
        owner_id=created_by_id,
    )
    db.add(contact)
    await db.flush()
    await db.refresh(contact)
    return contact


async def update_contact(
    db: AsyncSession, contact_id: int, data: ContactUpdate, updated_by_id: int | None = None
) -> Contact:
    contact = await get_contact_by_id(db, contact_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)
    contact.updated_by_id = updated_by_id
    await db.flush()
    await db.refresh(contact)
    return contact


async def delete_contact(db: AsyncSession, contact_id: int, deleted_by_id: int | None = None) -> None:
    contact = await get_contact_by_id(db, contact_id)
    contact.is_deleted = True
    contact.deleted_at = datetime.now(UTC)
    contact.deleted_by_id = deleted_by_id
    await db.flush()

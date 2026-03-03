from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.pagination import PaginationParams
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate


async def get_account_by_id(db: AsyncSession, account_id: int) -> Account:
    result = await db.execute(select(Account).where(Account.id == account_id, Account.is_deleted.is_(False)))
    account = result.scalars().first()
    if account is None:
        raise NotFoundError(f"Account {account_id} not found.")
    return account


async def list_accounts(
    db: AsyncSession,
    pagination: PaginationParams,
    name: str | None = None,
    type: str | None = None,
    industry: str | None = None,
) -> tuple[list[Account], int]:
    query = select(Account).where(Account.is_deleted.is_(False))
    if name:
        query = query.where(Account.name.ilike(f"%{name}%"))
    if type:
        query = query.where(Account.type == type)
    if industry:
        query = query.where(Account.industry.ilike(f"%{industry}%"))

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    query = query.order_by(Account.created_at.desc()).offset(pagination.offset).limit(pagination.limit)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def create_account(db: AsyncSession, data: AccountCreate, created_by_id: int | None = None) -> Account:
    account = Account(
        **data.model_dump(),
        created_by_id=created_by_id,
        updated_by_id=created_by_id,
        owner_id=created_by_id,
    )
    db.add(account)
    await db.flush()
    await db.refresh(account)
    return account


async def update_account(
    db: AsyncSession, account_id: int, data: AccountUpdate, updated_by_id: int | None = None
) -> Account:
    account = await get_account_by_id(db, account_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(account, field, value)
    account.updated_by_id = updated_by_id
    await db.flush()
    await db.refresh(account)
    return account


async def delete_account(db: AsyncSession, account_id: int, deleted_by_id: int | None = None) -> None:
    account = await get_account_by_id(db, account_id)
    account.is_deleted = True
    account.deleted_at = datetime.now(UTC)
    account.deleted_by_id = deleted_by_id
    await db.flush()

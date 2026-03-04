from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError
from app.core.pagination import PaginationParams
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).where(User.id == user_id, User.is_deleted.is_(False)))
    user = result.scalars().first()
    if user is None:
        raise NotFoundError(f"User {user_id} not found.")
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email, User.is_deleted.is_(False)))
    return result.scalars().first()


async def create_user(db: AsyncSession, data: UserCreate, created_by_id: int | None = None) -> User:
    existing = await get_user_by_email(db, data.email)
    if existing:
        raise ConflictError(f"A user with email '{data.email}' already exists.")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        created_by_id=created_by_id,
        updated_by_id=created_by_id,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    user = await get_user_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        raise AuthenticationError("Invalid email or password.")
    if not user.is_active:
        raise AuthenticationError("User account is inactive.")
    return user


async def update_user(db: AsyncSession, user_id: int, data: UserUpdate, updated_by_id: int | None = None) -> User:
    user = await get_user_by_id(db, user_id)
    update_data = data.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))
    for field, value in update_data.items():
        setattr(user, field, value)
    user.updated_by_id = updated_by_id
    await db.flush()
    await db.refresh(user)
    return user


async def list_users(
    db: AsyncSession,
    pagination: PaginationParams,
    *,
    is_active: bool | None = None,
    role_id: int | None = None,
    email_search: str | None = None,
) -> tuple[list[User], int]:
    query = select(User).where(User.is_deleted.is_(False))
    if is_active is not None:
        query = query.where(User.is_active.is_(is_active))
    if role_id is not None:
        query = query.where(User.role_id == role_id)
    if email_search:
        query = query.where(User.email.ilike(f"%{email_search}%"))

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    query = query.order_by(User.email.asc()).offset(pagination.offset).limit(pagination.limit)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def deactivate_user(db: AsyncSession, user_id: int, updated_by_id: int | None = None) -> User:
    user = await get_user_by_id(db, user_id)
    user.is_active = False
    user.updated_by_id = updated_by_id
    await db.flush()
    await db.refresh(user)
    return user

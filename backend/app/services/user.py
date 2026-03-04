"""Business logic for the User entity."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, ConflictError
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.base import CRUDService, escape_like


class UserService(CRUDService[User, UserCreate, UserUpdate]):
    model = User

    def apply_list_filters(self, query: Any, **filters: Any) -> Any:
        is_active = filters.get("is_active")
        if is_active is not None:
            query = query.where(User.is_active.is_(is_active))
        if role_id := filters.get("role_id"):
            query = query.where(User.role_id == role_id)
        if email := filters.get("email"):
            query = query.where(User.email.ilike(f"%{escape_like(email)}%", escape="\\"))
        return query

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email, User.is_deleted.is_(False)))
        return result.scalars().first()

    async def authenticate(self, db: AsyncSession, email: str, password: str) -> User:
        user = await self.get_by_email(db, email)
        if user is None or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password.")
        if not user.is_active:
            raise AuthenticationError("User account is inactive.")
        return user

    async def create(self, db: AsyncSession, data: UserCreate, created_by_id: int | None = None) -> User:
        existing = await self.get_by_email(db, data.email)
        if existing:
            raise ConflictError(f"A user with email '{data.email}' already exists.")

        payload = data.model_dump()
        payload["hashed_password"] = hash_password(payload.pop("password"))

        record = User(
            **payload,
            created_by_id=created_by_id,
            updated_by_id=created_by_id,
        )
        db.add(record)
        await db.flush()
        await db.refresh(record)
        return record

    async def update(
        self, db: AsyncSession, record_id: int, data: UserUpdate, updated_by_id: int | None = None
    ) -> User:
        record = await self.get_by_id(db, record_id)
        updates = data.model_dump(exclude_unset=True)
        if "password" in updates:
            updates["hashed_password"] = hash_password(updates.pop("password"))
        for field, value in updates.items():
            setattr(record, field, value)
        record.updated_by_id = updated_by_id
        await db.flush()
        await db.refresh(record)
        return record


user_service = UserService()

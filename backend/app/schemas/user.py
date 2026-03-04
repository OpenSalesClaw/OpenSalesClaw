from pydantic import BaseModel, EmailStr

from app.schemas.base import StandardReadFields


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    role_id: int | None = None


class UserRead(StandardReadFields):
    id: int
    email: str
    first_name: str | None
    last_name: str | None
    is_active: bool
    is_superuser: bool
    role_id: int | None = None


class UserList(StandardReadFields):
    """Lightweight user schema for list responses (no sensitive fields)."""

    id: int
    email: str
    first_name: str | None
    last_name: str | None
    is_active: bool
    is_superuser: bool
    role_id: int | None = None

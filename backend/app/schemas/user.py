from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.schemas.base import StandardReadFields


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None


class AdminUserCreate(BaseModel):
    """User creation schema for superuser admin endpoint."""

    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    role_id: int | None = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return v


class PasswordReset(BaseModel):
    """Schema for admin-initiated password reset."""

    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return v


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


class UserList(BaseModel):
    """Lightweight user schema for list responses (no audit/metadata clutter)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str | None
    last_name: str | None
    is_active: bool
    is_superuser: bool
    role_id: int | None = None

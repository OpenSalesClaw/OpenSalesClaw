from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.services.user import user_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRead:
    """Register a new user account. Disabled when ALLOW_PUBLIC_REGISTRATION=false."""
    if not settings.allow_public_registration:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Public registration is disabled. Contact an administrator to create an account.",
        )
    return UserRead.model_validate(await user_service.create(db, data))


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Authenticate with email + password and return an access token."""
    user = await user_service.authenticate(db, form_data.username, form_data.password)
    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
async def me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserRead:
    """Return the authenticated user's profile."""
    return UserRead.model_validate(current_user)

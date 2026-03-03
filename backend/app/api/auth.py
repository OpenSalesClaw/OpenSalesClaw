from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.exceptions import NotFoundError
from app.core.security import create_access_token
from app.schemas.user import UserCreate, UserRead
from app.services import user as user_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRead:
    """Register a new user account."""
    user = await user_service.create_user(db, data)
    return user  # type: ignore[return-value]


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Authenticate with email + password and return an access token."""
    try:
        user = await user_service.authenticate_user(db, form_data.username, form_data.password)
    except NotFoundError:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
async def me(
    current_user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRead:
    """Return the authenticated user's profile."""
    user = await user_service.get_user_by_id(db, current_user["id"])
    return user  # type: ignore[return-value]

"""Unit tests for the user service layer.

These tests exercise the service functions directly against the database session,
independently of the HTTP layer.  Each test is rolled back automatically by the
``db`` fixture in ``conftest.py``.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.schemas.user import UserCreate, UserUpdate
from app.services import user as user_service

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_USER_EMAIL = "svc_test@example.com"
_USER_PASSWORD = "servicepass123"


async def _make_user(db: AsyncSession, email: str = _USER_EMAIL, password: str = _USER_PASSWORD) -> object:
    data = UserCreate(email=email, password=password, first_name="Svc", last_name="Test")
    return await user_service.create_user(db, data)


# ---------------------------------------------------------------------------
# create_user
# ---------------------------------------------------------------------------


async def test_create_user_success(db: AsyncSession) -> None:
    user = await _make_user(db)
    assert user.id is not None
    assert user.email == _USER_EMAIL
    assert user.first_name == "Svc"
    assert user.last_name == "Test"
    assert user.is_active is True
    assert user.is_superuser is False


async def test_create_user_hashes_password(db: AsyncSession) -> None:
    user = await _make_user(db)
    assert user.hashed_password != _USER_PASSWORD
    assert len(user.hashed_password) > 20


async def test_create_user_duplicate_email_raises_conflict(db: AsyncSession) -> None:
    await _make_user(db)
    with pytest.raises(ConflictError):
        await _make_user(db)


async def test_create_user_minimal_fields(db: AsyncSession) -> None:
    data = UserCreate(email="minimal@example.com", password="pw")
    user = await user_service.create_user(db, data)
    assert user.id is not None
    assert user.first_name is None
    assert user.last_name is None


async def test_create_user_sets_standard_columns(db: AsyncSession) -> None:
    user = await _make_user(db)
    assert user.created_at is not None
    assert user.updated_at is not None
    assert user.is_deleted is False


# ---------------------------------------------------------------------------
# get_user_by_id
# ---------------------------------------------------------------------------


async def test_get_user_by_id_success(db: AsyncSession) -> None:
    created = await _make_user(db)
    fetched = await user_service.get_user_by_id(db, created.id)
    assert fetched.id == created.id
    assert fetched.email == _USER_EMAIL


async def test_get_user_by_id_not_found(db: AsyncSession) -> None:
    with pytest.raises(NotFoundError):
        await user_service.get_user_by_id(db, 999999999)


# ---------------------------------------------------------------------------
# get_user_by_email
# ---------------------------------------------------------------------------


async def test_get_user_by_email_success(db: AsyncSession) -> None:
    await _make_user(db)
    user = await user_service.get_user_by_email(db, _USER_EMAIL)
    assert user is not None
    assert user.email == _USER_EMAIL


async def test_get_user_by_email_not_found_returns_none(db: AsyncSession) -> None:
    result = await user_service.get_user_by_email(db, "nobody@example.com")
    assert result is None


# ---------------------------------------------------------------------------
# authenticate_user
# ---------------------------------------------------------------------------


async def test_authenticate_user_success(db: AsyncSession) -> None:
    await _make_user(db)
    user = await user_service.authenticate_user(db, _USER_EMAIL, _USER_PASSWORD)
    assert user.email == _USER_EMAIL


async def test_authenticate_user_wrong_password(db: AsyncSession) -> None:
    await _make_user(db)
    with pytest.raises(NotFoundError):
        await user_service.authenticate_user(db, _USER_EMAIL, "wrongpassword")


async def test_authenticate_user_unknown_email(db: AsyncSession) -> None:
    with pytest.raises(NotFoundError):
        await user_service.authenticate_user(db, "unknown@example.com", "whatever")


async def test_authenticate_user_inactive_account(db: AsyncSession) -> None:
    user = await _make_user(db)
    # Deactivate the user directly
    user.is_active = False
    await db.flush()
    with pytest.raises(NotFoundError):
        await user_service.authenticate_user(db, _USER_EMAIL, _USER_PASSWORD)


# ---------------------------------------------------------------------------
# update_user
# ---------------------------------------------------------------------------


async def test_update_user_name(db: AsyncSession) -> None:
    user = await _make_user(db)
    data = UserUpdate(first_name="Updated", last_name="Name")
    updated = await user_service.update_user(db, user.id, data)
    assert updated.first_name == "Updated"
    assert updated.last_name == "Name"


async def test_update_user_email(db: AsyncSession) -> None:
    user = await _make_user(db)
    data = UserUpdate(email="new_email@example.com")
    updated = await user_service.update_user(db, user.id, data)
    assert updated.email == "new_email@example.com"


async def test_update_user_password_is_rehashed(db: AsyncSession) -> None:
    user = await _make_user(db)
    old_hash = user.hashed_password
    data = UserUpdate(password="newpassword456")
    updated = await user_service.update_user(db, user.id, data)
    assert updated.hashed_password != old_hash
    assert updated.hashed_password != "newpassword456"


async def test_update_user_not_found(db: AsyncSession) -> None:
    data = UserUpdate(first_name="Ghost")
    with pytest.raises(NotFoundError):
        await user_service.update_user(db, 999999999, data)

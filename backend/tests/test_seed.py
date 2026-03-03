"""Tests for the application seeding module (``app.seed``)."""

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.contact import Contact
from app.models.lead import Lead
from app.models.user import User
from app.seed import (
    _ACCOUNTS,
    _CONTACTS,
    _LEADS,
    _SENTINEL_ACCOUNT,
    ensure_default_user,
    seed_demo_data,
)

# ---------------------------------------------------------------------------
# ensure_default_user
# ---------------------------------------------------------------------------


async def test_ensure_default_user_creates_user(db: AsyncSession, monkeypatch: pytest.MonkeyPatch) -> None:
    """Default admin user must be created when the DB is empty."""
    # Override credentials so we don't clash with other tests
    from app.core import config as cfg

    monkeypatch.setattr(cfg.settings, "default_admin_email", "seed_admin_test@example.com")
    monkeypatch.setattr(cfg.settings, "default_admin_password", "testpassword")

    user = await ensure_default_user(db)

    assert user.id is not None
    assert user.email == "seed_admin_test@example.com"
    assert user.is_superuser is True
    assert user.is_active is True
    # Self-referential audit columns must be set after creation
    assert user.created_by_id == user.id
    assert user.updated_by_id == user.id


async def test_ensure_default_user_idempotent(db: AsyncSession, monkeypatch: pytest.MonkeyPatch) -> None:
    """Calling ensure_default_user twice must not create a duplicate."""
    from app.core import config as cfg

    monkeypatch.setattr(cfg.settings, "default_admin_email", "seed_admin_idempotent@example.com")
    monkeypatch.setattr(cfg.settings, "default_admin_password", "testpassword")

    first = await ensure_default_user(db)
    second = await ensure_default_user(db)

    assert first.id == second.id

    result = await db.execute(
        select(func.count())
        .select_from(User)
        .where(
            User.email == "seed_admin_idempotent@example.com",
            User.is_deleted.is_(False),
        )
    )
    assert result.scalar_one() == 1


# ---------------------------------------------------------------------------
# seed_demo_data — disabled
# ---------------------------------------------------------------------------


async def test_seed_demo_data_skipped_when_disabled(db: AsyncSession, monkeypatch: pytest.MonkeyPatch) -> None:
    """Demo data must not be inserted when SEED_DEMO_DATA is False."""
    from app.core import config as cfg

    monkeypatch.setattr(cfg.settings, "seed_demo_data", False)
    monkeypatch.setattr(cfg.settings, "default_admin_email", "seed_disabled_admin@example.com")
    monkeypatch.setattr(cfg.settings, "default_admin_password", "testpassword")

    admin = await ensure_default_user(db)
    await seed_demo_data(db, admin)

    result = await db.execute(select(func.count()).select_from(Account).where(Account.is_deleted.is_(False)))
    assert result.scalar_one() == 0


# ---------------------------------------------------------------------------
# seed_demo_data — enabled
# ---------------------------------------------------------------------------


async def test_seed_demo_data_inserts_correct_counts(db: AsyncSession, monkeypatch: pytest.MonkeyPatch) -> None:
    """Demo data must insert the expected number of accounts, contacts, and leads."""
    from app.core import config as cfg

    monkeypatch.setattr(cfg.settings, "seed_demo_data", True)
    monkeypatch.setattr(cfg.settings, "default_admin_email", "seed_counts_admin@example.com")
    monkeypatch.setattr(cfg.settings, "default_admin_password", "testpassword")

    admin = await ensure_default_user(db)
    await seed_demo_data(db, admin)

    account_count = (
        await db.execute(select(func.count()).select_from(Account).where(Account.is_deleted.is_(False)))
    ).scalar_one()
    contact_count = (
        await db.execute(select(func.count()).select_from(Contact).where(Contact.is_deleted.is_(False)))
    ).scalar_one()
    lead_count = (
        await db.execute(select(func.count()).select_from(Lead).where(Lead.is_deleted.is_(False)))
    ).scalar_one()

    assert account_count == len(_ACCOUNTS)
    assert contact_count == len(_CONTACTS)
    assert lead_count == len(_LEADS)


async def test_seed_demo_data_sets_audit_columns(db: AsyncSession, monkeypatch: pytest.MonkeyPatch) -> None:
    """All seeded records must have owner_id and created_by_id set to the admin user."""
    from app.core import config as cfg

    monkeypatch.setattr(cfg.settings, "seed_demo_data", True)
    monkeypatch.setattr(cfg.settings, "default_admin_email", "seed_audit_admin@example.com")
    monkeypatch.setattr(cfg.settings, "default_admin_password", "testpassword")

    admin = await ensure_default_user(db)
    await seed_demo_data(db, admin)

    result = await db.execute(select(Account).where(Account.name == _SENTINEL_ACCOUNT, Account.is_deleted.is_(False)))
    sentinel = result.scalars().first()
    assert sentinel is not None
    assert sentinel.owner_id == admin.id
    assert sentinel.created_by_id == admin.id
    assert sentinel.updated_by_id == admin.id


async def test_seed_demo_data_idempotent(db: AsyncSession, monkeypatch: pytest.MonkeyPatch) -> None:
    """Calling seed_demo_data twice must not insert duplicate records."""
    from app.core import config as cfg

    monkeypatch.setattr(cfg.settings, "seed_demo_data", True)
    monkeypatch.setattr(cfg.settings, "default_admin_email", "seed_idempotent2_admin@example.com")
    monkeypatch.setattr(cfg.settings, "default_admin_password", "testpassword")

    admin = await ensure_default_user(db)
    await seed_demo_data(db, admin)
    await seed_demo_data(db, admin)  # second call should be a no-op

    account_count = (
        await db.execute(select(func.count()).select_from(Account).where(Account.is_deleted.is_(False)))
    ).scalar_one()
    assert account_count == len(_ACCOUNTS)


async def test_seed_demo_data_contacts_linked_to_accounts(db: AsyncSession, monkeypatch: pytest.MonkeyPatch) -> None:
    """Contacts must be linked to their parent account via account_id."""
    from app.core import config as cfg

    monkeypatch.setattr(cfg.settings, "seed_demo_data", True)
    monkeypatch.setattr(cfg.settings, "default_admin_email", "seed_links_admin@example.com")
    monkeypatch.setattr(cfg.settings, "default_admin_password", "testpassword")

    admin = await ensure_default_user(db)
    await seed_demo_data(db, admin)

    # Every contact in our demo data is linked to a known account
    result = await db.execute(
        select(func.count())
        .select_from(Contact)
        .where(
            Contact.account_id.is_(None),
            Contact.is_deleted.is_(False),
        )
    )
    unlinked = result.scalar_one()
    assert unlinked == 0, f"{unlinked} contacts have no account_id"

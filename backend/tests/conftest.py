"""Shared test fixtures for the OpenSalesClaw test suite.

Strategy:
- A single async SQLAlchemy engine is created once per session against a dedicated
  test database (``opensalesclaw_test``).  All tables are created at the start of
  the session and dropped at the end.
- Each test function receives an ``AsyncSession`` that is bound to a connection
  with an outer ``BEGIN`` and an inner ``SAVEPOINT``.  When the test ends the
  outer transaction is rolled back, leaving the database clean for the next test.
- The FastAPI ``get_db`` dependency is overridden for every test client so that
  every database call in a request shares the same session (and therefore sees
  in-flight, not-yet-committed test data).
"""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.models  # noqa: F401 – ensure all models are registered on Base.metadata
from app.core.database import get_db
from app.main import app
from app.models.base import Base

# ---------------------------------------------------------------------------
# Test database URL — override via env var TEST_DATABASE_URL if needed.
# ---------------------------------------------------------------------------
import os

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/opensalesclaw_test",
)


# ---------------------------------------------------------------------------
# Session-scoped engine — tables created/dropped once per pytest run.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
async def test_engine():
    """Create the async engine and materialise all tables in the test DB."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


# ---------------------------------------------------------------------------
# Function-scoped database session — every test gets a rolled-back transaction.
# ---------------------------------------------------------------------------


@pytest.fixture
async def db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide an ``AsyncSession`` whose changes are rolled back after each test.

    Uses ``join_transaction_mode="create_savepoint"`` so that ``session.commit()``
    inside route handlers releases a SAVEPOINT rather than the outer transaction,
    which is rolled back at test teardown.
    """
    async with test_engine.connect() as conn:
        await conn.begin()
        session_factory = async_sessionmaker(
            bind=conn,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
            join_transaction_mode="create_savepoint",
        )
        async with session_factory() as session:
            yield session
        await conn.rollback()


# ---------------------------------------------------------------------------
# HTTP test client with get_db overridden.
# ---------------------------------------------------------------------------


@pytest.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an ``httpx.AsyncClient`` wired to the test session."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.pop(get_db, None)


# ---------------------------------------------------------------------------
# Authenticated user helpers.
# ---------------------------------------------------------------------------

_TEST_USER_EMAIL = "testuser@example.com"
_TEST_USER_PASSWORD = "testpassword123"


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    """Register a test user and return valid ``Authorization`` headers."""
    await client.post(
        "/api/auth/register",
        json={
            "email": _TEST_USER_EMAIL,
            "password": _TEST_USER_PASSWORD,
            "first_name": "Test",
            "last_name": "User",
        },
    )
    resp = await client.post(
        "/api/auth/login",
        data={"username": _TEST_USER_EMAIL, "password": _TEST_USER_PASSWORD},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

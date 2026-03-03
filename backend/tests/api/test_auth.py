"""Tests for authentication endpoints: register, login, me."""

import pytest
from httpx import AsyncClient


@pytest.fixture
async def registered_user(client: AsyncClient) -> dict:
    """Register a dedicated user for auth tests and return the response body."""
    resp = await client.post(
        "/api/auth/register",
        json={
            "email": "auth_test@example.com",
            "password": "securepass123",
            "first_name": "Auth",
            "last_name": "Tester",
        },
    )
    assert resp.status_code == 201
    return resp.json()


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------


async def test_register_success(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/auth/register",
        json={"email": "new@example.com", "password": "secret123", "first_name": "New", "last_name": "User"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "new@example.com"
    assert data["first_name"] == "New"
    assert data["last_name"] == "User"
    assert "id" in data
    assert "hashed_password" not in data


async def test_register_minimal_fields(client: AsyncClient) -> None:
    """Only email + password are required."""
    resp = await client.post(
        "/api/auth/register",
        json={"email": "minimal@example.com", "password": "pw"},
    )
    assert resp.status_code == 201
    assert resp.json()["first_name"] is None


async def test_register_duplicate_email(client: AsyncClient) -> None:
    payload = {"email": "dup@example.com", "password": "secret123"}
    r1 = await client.post("/api/auth/register", json=payload)
    assert r1.status_code == 201
    r2 = await client.post("/api/auth/register", json=payload)
    assert r2.status_code == 409


async def test_register_invalid_email(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/auth/register",
        json={"email": "not-an-email", "password": "secret123"},
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


async def test_login_success(client: AsyncClient, registered_user: dict) -> None:
    resp = await client.post(
        "/api/auth/login",
        data={"username": "auth_test@example.com", "password": "securepass123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient, registered_user: dict) -> None:
    resp = await client.post(
        "/api/auth/login",
        data={"username": "auth_test@example.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 401


async def test_login_unknown_user(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/auth/login",
        data={"username": "nobody@example.com", "password": "whatever"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Me
# ---------------------------------------------------------------------------


async def test_me_returns_current_user(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data
    assert "hashed_password" not in data


async def test_me_unauthenticated(client: AsyncClient) -> None:
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 401


async def test_me_invalid_token(client: AsyncClient) -> None:
    resp = await client.get("/api/auth/me", headers={"Authorization": "Bearer notavalidtoken"})
    assert resp.status_code == 401

"""Tests for User admin CRUD endpoints.

Covers: list (admin-only), get by ID, update (admin-only), deactivate (admin-only),
RBAC enforcement (non-admin gets 403), and auth requirements.
"""

from httpx import AsyncClient

# ---------------------------------------------------------------------------
# List users (admin-only)
# ---------------------------------------------------------------------------


async def test_list_users_as_superuser(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    resp = await client.get("/api/users", headers=superuser_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1  # at least the superuser itself


async def test_list_users_non_admin_gets_403(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.get("/api/users", headers=auth_headers)
    assert resp.status_code == 403


async def test_list_users_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/users")
    assert resp.status_code == 401


async def test_list_users_filter_by_active(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    resp = await client.get("/api/users?is_active=true", headers=superuser_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert all(item["is_active"] for item in data["items"])


async def test_list_users_filter_by_email(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    resp = await client.get("/api/users?email=superuser", headers=superuser_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert all("superuser" in item["email"] for item in data["items"])


async def test_list_users_pagination(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    # Register a few additional users
    for i in range(3):
        await client.post(
            "/api/auth/register",
            json={"email": f"extra{i}@example.com", "password": "pass1234"},
        )
    resp = await client.get("/api/users?limit=2&offset=0", headers=superuser_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) <= 2


# ---------------------------------------------------------------------------
# Get by ID
# ---------------------------------------------------------------------------


async def test_get_user_by_id(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    # Get own profile first via /me equivalent
    me_resp = await client.get("/api/auth/me", headers=auth_headers)
    assert me_resp.status_code == 200
    user_id = me_resp.json()["id"]

    resp = await client.get(f"/api/users/{user_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == user_id


async def test_get_user_not_found(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    resp = await client.get("/api/users/999999999", headers=superuser_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Update (admin-only)
# ---------------------------------------------------------------------------


async def test_update_user_as_superuser(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    # Register a user to update
    reg = await client.post(
        "/api/auth/register",
        json={"email": "updateme@example.com", "password": "pass1234", "first_name": "Old"},
    )
    user_id = reg.json()["id"]
    resp = await client.patch(f"/api/users/{user_id}", json={"first_name": "Updated"}, headers=superuser_headers)
    assert resp.status_code == 200
    assert resp.json()["first_name"] == "Updated"


async def test_update_user_non_admin_gets_403(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    me_resp = await client.get("/api/auth/me", headers=auth_headers)
    user_id = me_resp.json()["id"]
    resp = await client.patch(f"/api/users/{user_id}", json={"first_name": "Hack"}, headers=auth_headers)
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Deactivate (admin-only)
# ---------------------------------------------------------------------------


async def test_deactivate_user(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    reg = await client.post(
        "/api/auth/register",
        json={"email": "deactivateme@example.com", "password": "pass1234"},
    )
    user_id = reg.json()["id"]
    resp = await client.delete(f"/api/users/{user_id}", headers=superuser_headers)
    assert resp.status_code == 204

    # Verify user is now inactive
    get_resp = await client.get(f"/api/users/{user_id}", headers=superuser_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["is_active"] is False


async def test_deactivate_user_non_admin_gets_403(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    me_resp = await client.get("/api/auth/me", headers=auth_headers)
    user_id = me_resp.json()["id"]
    resp = await client.delete(f"/api/users/{user_id}", headers=auth_headers)
    assert resp.status_code == 403


async def test_deactivate_user_not_found(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    resp = await client.delete("/api/users/999999999", headers=superuser_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# /users/me endpoint
# ---------------------------------------------------------------------------


async def test_get_me(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.get("/api/users/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "email" in data
    assert "id" in data

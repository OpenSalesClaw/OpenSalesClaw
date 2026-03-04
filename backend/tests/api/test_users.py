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


async def test_delete_user(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    reg = await client.post(
        "/api/auth/register",
        json={"email": "deleteme@example.com", "password": "pass1234"},
    )
    user_id = reg.json()["id"]
    resp = await client.delete(f"/api/users/{user_id}", headers=superuser_headers)
    assert resp.status_code == 204

    # User is soft-deleted — no longer accessible
    get_resp = await client.get(f"/api/users/{user_id}", headers=superuser_headers)
    assert get_resp.status_code == 404


async def test_delete_user_non_admin_gets_403(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    me_resp = await client.get("/api/auth/me", headers=auth_headers)
    user_id = me_resp.json()["id"]
    resp = await client.delete(f"/api/users/{user_id}", headers=auth_headers)
    assert resp.status_code == 403


async def test_delete_user_not_found(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    resp = await client.delete("/api/users/999999999", headers=superuser_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Admin create user (POST /api/users)
# ---------------------------------------------------------------------------


async def test_admin_create_user(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    resp = await client.post(
        "/api/users",
        json={"email": "newadmin@example.com", "password": "securepass1", "first_name": "New", "last_name": "User"},
        headers=superuser_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "newadmin@example.com"
    assert data["first_name"] == "New"
    assert data["is_active"] is True
    assert data["is_superuser"] is False


async def test_admin_create_superuser(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    resp = await client.post(
        "/api/users",
        json={"email": "newsuper@example.com", "password": "securepass1", "is_superuser": True},
        headers=superuser_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["is_superuser"] is True


async def test_admin_create_user_duplicate_email(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    payload = {"email": "dupuser@example.com", "password": "securepass1"}
    await client.post("/api/users", json=payload, headers=superuser_headers)
    resp = await client.post("/api/users", json=payload, headers=superuser_headers)
    assert resp.status_code == 409


async def test_admin_create_user_non_admin_gets_403(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.post(
        "/api/users",
        json={"email": "blocked@example.com", "password": "securepass1"},
        headers=auth_headers,
    )
    assert resp.status_code == 403


async def test_admin_create_user_requires_auth(client: AsyncClient) -> None:
    resp = await client.post("/api/users", json={"email": "x@example.com", "password": "securepass1"})
    assert resp.status_code == 401


async def test_admin_create_user_weak_password(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    resp = await client.post(
        "/api/users",
        json={"email": "weak@example.com", "password": "short"},
        headers=superuser_headers,
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Password reset (PATCH /api/users/{id}/reset-password)
# ---------------------------------------------------------------------------


async def test_reset_user_password(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    reg = await client.post(
        "/api/auth/register",
        json={"email": "resetme@example.com", "password": "oldpassword"},
    )
    user_id = reg.json()["id"]

    resp = await client.patch(
        f"/api/users/{user_id}/reset-password",
        json={"new_password": "newpassword99"},
        headers=superuser_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == user_id

    # Can now log in with the new password
    login = await client.post(
        "/api/auth/login",
        data={"username": "resetme@example.com", "password": "newpassword99"},
    )
    assert login.status_code == 200


async def test_reset_password_non_admin_gets_403(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    me_resp = await client.get("/api/auth/me", headers=auth_headers)
    user_id = me_resp.json()["id"]
    resp = await client.patch(
        f"/api/users/{user_id}/reset-password",
        json={"new_password": "newpassword99"},
        headers=auth_headers,
    )
    assert resp.status_code == 403


async def test_reset_password_weak_password(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    reg = await client.post(
        "/api/auth/register",
        json={"email": "weakreset@example.com", "password": "pass1234"},
    )
    user_id = reg.json()["id"]
    resp = await client.patch(
        f"/api/users/{user_id}/reset-password",
        json={"new_password": "weak"},
        headers=superuser_headers,
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Self-deletion / self-deactivation guards
# ---------------------------------------------------------------------------


async def test_delete_own_account_gets_400(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    me_resp = await client.get("/api/auth/me", headers=superuser_headers)
    user_id = me_resp.json()["id"]
    resp = await client.delete(f"/api/users/{user_id}", headers=superuser_headers)
    assert resp.status_code == 400


async def test_deactivate_own_account_gets_400(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    me_resp = await client.get("/api/auth/me", headers=superuser_headers)
    user_id = me_resp.json()["id"]
    resp = await client.patch(f"/api/users/{user_id}", json={"is_active": False}, headers=superuser_headers)
    assert resp.status_code == 400


async def test_remove_own_superuser_gets_400(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    me_resp = await client.get("/api/auth/me", headers=superuser_headers)
    user_id = me_resp.json()["id"]
    resp = await client.patch(f"/api/users/{user_id}", json={"is_superuser": False}, headers=superuser_headers)
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Docstring only - /users/me removed; use /api/auth/me instead
# ---------------------------------------------------------------------------

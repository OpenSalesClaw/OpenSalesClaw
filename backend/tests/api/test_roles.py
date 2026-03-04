"""Tests for Role CRUD endpoints.

Covers: list, create (superuser-only), get by ID, update, delete, hierarchy,
circular reference prevention, and RBAC enforcement.
"""

from httpx import AsyncClient

from tests.helpers import create_role


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


async def test_list_roles_empty(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.get("/api/roles", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


async def test_list_roles_returns_created(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    await create_role(client, superuser_headers, name="Sales Manager")
    resp = await client.get("/api/roles", headers=superuser_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Sales Manager"


async def test_list_roles_accessible_to_non_admin(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.get("/api/roles", headers=auth_headers)
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Create (superuser-only)
# ---------------------------------------------------------------------------


async def test_create_role_minimal(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    resp = await client.post("/api/roles", json={"name": "CEO"}, headers=superuser_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "CEO"
    assert data["parent_role_id"] is None


async def test_create_role_with_parent(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    parent = await create_role(client, superuser_headers, name="VP Sales")
    resp = await client.post(
        "/api/roles",
        json={"name": "Sales Rep", "parent_role_id": parent["id"], "description": "Front-line sales"},
        headers=superuser_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["parent_role_id"] == parent["id"]


async def test_create_role_non_admin_gets_403(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.post("/api/roles", json={"name": "Blocked"}, headers=auth_headers)
    assert resp.status_code == 403


async def test_create_role_requires_auth(client: AsyncClient) -> None:
    resp = await client.post("/api/roles", json={"name": "No Auth"})
    assert resp.status_code == 401


async def test_create_role_requires_name(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    resp = await client.post("/api/roles", json={"description": "No name"}, headers=superuser_headers)
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Get by ID
# ---------------------------------------------------------------------------


async def test_get_role_by_id(client: AsyncClient, auth_headers: dict[str, str], superuser_headers: dict[str, str]) -> None:
    role = await create_role(client, superuser_headers, name="CTO")
    resp = await client.get(f"/api/roles/{role['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == role["id"]
    assert resp.json()["name"] == "CTO"


async def test_get_role_not_found(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.get("/api/roles/999999999", headers=auth_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


async def test_update_role(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    role = await create_role(client, superuser_headers, name="Old Role Name")
    resp = await client.patch(f"/api/roles/{role['id']}", json={"name": "New Role Name"}, headers=superuser_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Role Name"


async def test_update_role_non_admin_gets_403(client: AsyncClient, auth_headers: dict[str, str], superuser_headers: dict[str, str]) -> None:
    role = await create_role(client, superuser_headers, name="Should Not Change")
    resp = await client.patch(f"/api/roles/{role['id']}", json={"name": "Hacked"}, headers=auth_headers)
    assert resp.status_code == 403


async def test_update_role_not_found(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    resp = await client.patch("/api/roles/999999999", json={"name": "Ghost"}, headers=superuser_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Hierarchy
# ---------------------------------------------------------------------------


async def test_hierarchy_endpoint(client: AsyncClient, auth_headers: dict[str, str], superuser_headers: dict[str, str]) -> None:
    parent = await create_role(client, superuser_headers, name="Hierarchy VP")
    await client.post(
        "/api/roles",
        json={"name": "Hierarchy Rep", "parent_role_id": parent["id"]},
        headers=superuser_headers,
    )
    resp = await client.get("/api/roles/hierarchy", headers=auth_headers)
    assert resp.status_code == 200
    hierarchy = resp.json()
    assert isinstance(hierarchy, list)
    names = {item["name"] for item in hierarchy}
    assert "Hierarchy VP" in names
    assert "Hierarchy Rep" in names


# ---------------------------------------------------------------------------
# Circular reference prevention
# ---------------------------------------------------------------------------


async def test_circular_parent_self_reference(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    role = await create_role(client, superuser_headers, name="Solo Role")
    resp = await client.patch(
        f"/api/roles/{role['id']}",
        json={"parent_role_id": role["id"]},
        headers=superuser_headers,
    )
    assert resp.status_code == 409


async def test_circular_parent_chain(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    # A -> B -> A would be circular
    a = await create_role(client, superuser_headers, name="Circular A")
    b_resp = await client.post(
        "/api/roles",
        json={"name": "Circular B", "parent_role_id": a["id"]},
        headers=superuser_headers,
    )
    b = b_resp.json()
    # Now try to set A's parent to B — creating a cycle
    resp = await client.patch(
        f"/api/roles/{a['id']}",
        json={"parent_role_id": b["id"]},
        headers=superuser_headers,
    )
    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# Soft delete
# ---------------------------------------------------------------------------


async def test_soft_delete_role(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    role = await create_role(client, superuser_headers, name="Delete Me Role")
    resp = await client.delete(f"/api/roles/{role['id']}", headers=superuser_headers)
    assert resp.status_code == 204


async def test_deleted_role_returns_404(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    role = await create_role(client, superuser_headers, name="Gone Role")
    await client.delete(f"/api/roles/{role['id']}", headers=superuser_headers)
    resp = await client.get(f"/api/roles/{role['id']}", headers=superuser_headers)
    assert resp.status_code == 404


async def test_delete_role_non_admin_gets_403(client: AsyncClient, auth_headers: dict[str, str], superuser_headers: dict[str, str]) -> None:
    role = await create_role(client, superuser_headers, name="Protected Role")
    resp = await client.delete(f"/api/roles/{role['id']}", headers=auth_headers)
    assert resp.status_code == 403

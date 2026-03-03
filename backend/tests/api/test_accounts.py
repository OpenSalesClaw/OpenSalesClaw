"""Tests for Account CRUD endpoints.

Covers: list (empty + paginated + filtered), create, get by ID, update,
soft delete, 404 on deleted/missing, and auth requirement.
"""

import pytest
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


async def _create_account(client: AsyncClient, headers: dict[str, str], **kwargs) -> dict:
    payload = {"name": "Test Account", **kwargs}
    resp = await client.post("/api/accounts", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


async def test_list_accounts_empty(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.get("/api/accounts", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["offset"] == 0
    assert data["limit"] == 20


async def test_list_accounts_returns_created(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    await _create_account(client, auth_headers, name="Acme Corp")
    resp = await client.get("/api/accounts", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Acme Corp"


async def test_list_accounts_pagination(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    for i in range(5):
        await _create_account(client, auth_headers, name=f"Paged Account {i}")
    resp = await client.get("/api/accounts?limit=2&offset=0", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["limit"] == 2
    assert data["offset"] == 0


async def test_list_accounts_filter_by_name(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    await _create_account(client, auth_headers, name="Globocorp")
    await _create_account(client, auth_headers, name="TechStart")
    resp = await client.get("/api/accounts?name=Globo", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Globocorp"


async def test_list_accounts_filter_by_type(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    await _create_account(client, auth_headers, name="CustomerCo", type="Customer")
    await _create_account(client, auth_headers, name="PartnerCo", type="Partner")
    resp = await client.get("/api/accounts?type=Customer", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert all(item["type"] == "Customer" for item in data["items"])


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


async def test_create_account_minimal(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.post("/api/accounts", json={"name": "Minimal Corp"}, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Minimal Corp"
    assert "id" in data
    assert data["type"] is None


async def test_create_account_full(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    payload = {
        "name": "Full Corp",
        "type": "Customer",
        "industry": "Technology",
        "website": "https://fullcorp.example.com",
        "phone": "+1-555-0100",
        "billing_city": "San Francisco",
        "billing_state": "CA",
        "billing_country": "US",
        "annual_revenue": "1000000.00",
        "number_of_employees": 50,
    }
    resp = await client.post("/api/accounts", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["industry"] == "Technology"
    assert data["billing_city"] == "San Francisco"
    assert data["number_of_employees"] == 50


async def test_create_account_requires_name(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.post("/api/accounts", json={"type": "Customer"}, headers=auth_headers)
    assert resp.status_code == 422


async def test_create_account_sets_created_by(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.post("/api/accounts", json={"name": "Audit Corp"}, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["created_by_id"] is not None


# ---------------------------------------------------------------------------
# Get by ID
# ---------------------------------------------------------------------------


async def test_get_account_by_id(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    account = await _create_account(client, auth_headers, name="Fetch Me")
    resp = await client.get(f"/api/accounts/{account['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == account["id"]
    assert resp.json()["name"] == "Fetch Me"


async def test_get_account_not_found(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.get("/api/accounts/999999999", headers=auth_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


async def test_update_account_name(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    account = await _create_account(client, auth_headers, name="Old Name")
    resp = await client.patch(
        f"/api/accounts/{account['id']}", json={"name": "New Name"}, headers=auth_headers
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


async def test_update_account_partial(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    account = await _create_account(client, auth_headers, name="Partial Update", type="Customer")
    resp = await client.patch(
        f"/api/accounts/{account['id']}", json={"industry": "Finance"}, headers=auth_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Partial Update"  # unchanged
    assert data["type"] == "Customer"  # unchanged
    assert data["industry"] == "Finance"  # updated


async def test_update_account_not_found(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.patch("/api/accounts/999999999", json={"name": "Ghost"}, headers=auth_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Soft delete
# ---------------------------------------------------------------------------


async def test_soft_delete_account(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    account = await _create_account(client, auth_headers, name="Delete Me")
    del_resp = await client.delete(f"/api/accounts/{account['id']}", headers=auth_headers)
    assert del_resp.status_code == 204


async def test_deleted_account_returns_404(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    account = await _create_account(client, auth_headers, name="Gone Soon")
    await client.delete(f"/api/accounts/{account['id']}", headers=auth_headers)
    resp = await client.get(f"/api/accounts/{account['id']}", headers=auth_headers)
    assert resp.status_code == 404


async def test_deleted_account_excluded_from_list(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    account = await _create_account(client, auth_headers, name="Will Be Deleted")
    await client.delete(f"/api/accounts/{account['id']}", headers=auth_headers)
    resp = await client.get("/api/accounts", headers=auth_headers)
    ids = [item["id"] for item in resp.json()["items"]]
    assert account["id"] not in ids


async def test_delete_account_not_found(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.delete("/api/accounts/999999999", headers=auth_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Auth requirement
# ---------------------------------------------------------------------------


async def test_accounts_require_auth_list(client: AsyncClient) -> None:
    resp = await client.get("/api/accounts")
    assert resp.status_code == 401


async def test_accounts_require_auth_create(client: AsyncClient) -> None:
    resp = await client.post("/api/accounts", json={"name": "Unauth"})
    assert resp.status_code == 401

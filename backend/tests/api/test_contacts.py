"""Tests for Contact CRUD endpoints.

Covers: list (empty + paginated + filtered by account_id/last_name/email),
create (with and without account link), get by ID, update, soft delete,
and auth requirement.
"""

from httpx import AsyncClient

from tests.helpers import create_account, create_contact

# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


async def test_list_contacts_empty(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.get("/api/contacts", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


async def test_list_contacts_returns_created(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    await create_contact(client, auth_headers, first_name="Jane", last_name="Smith")
    resp = await client.get("/api/contacts", headers=auth_headers)
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["last_name"] == "Smith"


async def test_list_contacts_pagination(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    for i in range(4):
        await create_contact(client, auth_headers, last_name=f"Page{i}")
    resp = await client.get("/api/contacts?limit=2&offset=0", headers=auth_headers)
    data = resp.json()
    assert len(data["items"]) == 2
    assert data["total"] == 4


async def test_list_contacts_filter_by_last_name(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    await create_contact(client, auth_headers, last_name="Anderson")
    await create_contact(client, auth_headers, last_name="Bradley")
    resp = await client.get("/api/contacts?last_name=Ander", headers=auth_headers)
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["last_name"] == "Anderson"


async def test_list_contacts_filter_by_email(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    await create_contact(client, auth_headers, last_name="Mailer", email="mailer@corp.example.com")
    await create_contact(client, auth_headers, last_name="Other", email="other@example.com")
    resp = await client.get("/api/contacts?email=mailer", headers=auth_headers)
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["last_name"] == "Mailer"


async def test_list_contacts_filter_by_account_id(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    account = await create_account(client, auth_headers, name="FilterCo")
    await create_contact(client, auth_headers, last_name="Linked", account_id=account["id"])
    await create_contact(client, auth_headers, last_name="Unlinked")
    resp = await client.get(f"/api/contacts?account_id={account['id']}", headers=auth_headers)
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["last_name"] == "Linked"
    assert data["items"][0]["account_id"] == account["id"]


# ---------------------------------------------------------------------------
# Account relationship
# ---------------------------------------------------------------------------


async def testcreate_contact_linked_to_account(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    account = await create_account(client, auth_headers, name="Parent Corp")
    contact = await create_contact(client, auth_headers, last_name="Employee", account_id=account["id"])
    assert contact["account_id"] == account["id"]


async def testcreate_contact_without_account(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    contact = await create_contact(client, auth_headers, last_name="Standalone")
    assert contact["account_id"] is None


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


async def testcreate_contact_full(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    payload = {
        "first_name": "John",
        "last_name": "Full",
        "email": "john.full@example.com",
        "phone": "+1-555-0200",
        "title": "Engineer",
        "department": "R&D",
        "mailing_city": "Austin",
        "mailing_country": "US",
    }
    resp = await client.post("/api/contacts", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Engineer"
    assert data["mailing_city"] == "Austin"


async def testcreate_contact_requires_last_name(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.post("/api/contacts", json={"first_name": "NoLast"}, headers=auth_headers)
    assert resp.status_code == 422


async def testcreate_contact_sets_created_by(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    contact = await create_contact(client, auth_headers, last_name="Audited")
    assert contact["created_by_id"] is not None


# ---------------------------------------------------------------------------
# Get by ID
# ---------------------------------------------------------------------------


async def test_get_contact_by_id(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    contact = await create_contact(client, auth_headers, last_name="Fetch")
    resp = await client.get(f"/api/contacts/{contact['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == contact["id"]


async def test_get_contact_not_found(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.get("/api/contacts/999999999", headers=auth_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


async def test_update_contact(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    contact = await create_contact(client, auth_headers, last_name="Before")
    resp = await client.patch(f"/api/contacts/{contact['id']}", json={"last_name": "After"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["last_name"] == "After"


async def test_update_contact_partial_preserves_fields(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    contact = await create_contact(client, auth_headers, last_name="Preserve", email="keep@example.com")
    resp = await client.patch(f"/api/contacts/{contact['id']}", json={"title": "Manager"}, headers=auth_headers)
    data = resp.json()
    assert data["email"] == "keep@example.com"  # unchanged
    assert data["title"] == "Manager"


async def test_update_contact_not_found(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.patch("/api/contacts/999999999", json={"last_name": "Ghost"}, headers=auth_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Soft delete
# ---------------------------------------------------------------------------


async def test_soft_delete_contact(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    contact = await create_contact(client, auth_headers, last_name="Deleted")
    resp = await client.delete(f"/api/contacts/{contact['id']}", headers=auth_headers)
    assert resp.status_code == 204


async def test_deleted_contact_returns_404(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    contact = await create_contact(client, auth_headers, last_name="Gone")
    await client.delete(f"/api/contacts/{contact['id']}", headers=auth_headers)
    resp = await client.get(f"/api/contacts/{contact['id']}", headers=auth_headers)
    assert resp.status_code == 404


async def test_deleted_contact_excluded_from_list(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    contact = await create_contact(client, auth_headers, last_name="RemoveMe")
    await client.delete(f"/api/contacts/{contact['id']}", headers=auth_headers)
    resp = await client.get("/api/contacts", headers=auth_headers)
    ids = [item["id"] for item in resp.json()["items"]]
    assert contact["id"] not in ids


# ---------------------------------------------------------------------------
# Auth requirement
# ---------------------------------------------------------------------------


async def test_contacts_require_auth_list(client: AsyncClient) -> None:
    resp = await client.get("/api/contacts")
    assert resp.status_code == 401


async def test_contacts_require_auth_create(client: AsyncClient) -> None:
    resp = await client.post("/api/contacts", json={"last_name": "Unauth"})
    assert resp.status_code == 401

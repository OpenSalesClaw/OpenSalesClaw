"""Tests for Lead CRUD endpoints.

Covers: list (empty + paginated + filtered by status/company/email),
create, get by ID, update, soft delete, and auth requirement.
"""

from httpx import AsyncClient

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


async def _create_lead(client: AsyncClient, headers: dict[str, str], **kwargs) -> dict:
    payload = {"last_name": "Lead", "company": "LeadCo", **kwargs}
    resp = await client.post("/api/leads", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


async def test_list_leads_empty(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.get("/api/leads", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


async def test_list_leads_returns_created(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    await _create_lead(client, auth_headers, last_name="Johnson", company="JohnsonInc")
    resp = await client.get("/api/leads", headers=auth_headers)
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["last_name"] == "Johnson"


async def test_list_leads_pagination(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    for i in range(5):
        await _create_lead(client, auth_headers, last_name=f"Lead{i}", company=f"Co{i}")
    resp = await client.get("/api/leads?limit=3&offset=0", headers=auth_headers)
    data = resp.json()
    assert len(data["items"]) == 3
    assert data["total"] == 5


async def test_list_leads_filter_by_status(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    await _create_lead(client, auth_headers, last_name="NewLead", company="NewCo", status="New")
    await _create_lead(client, auth_headers, last_name="ContactedLead", company="ContactedCo", status="Contacted")
    resp = await client.get("/api/leads?status=New", headers=auth_headers)
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["status"] == "New"


async def test_list_leads_filter_by_company(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    await _create_lead(client, auth_headers, last_name="A", company="UniqueWidgets")
    await _create_lead(client, auth_headers, last_name="B", company="OtherInc")
    resp = await client.get("/api/leads?company=UniqueW", headers=auth_headers)
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["company"] == "UniqueWidgets"


async def test_list_leads_filter_by_email(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    await _create_lead(client, auth_headers, last_name="Emailer", company="Co", email="special@leads.example.com")
    await _create_lead(client, auth_headers, last_name="Other", company="Co2", email="other@example.com")
    resp = await client.get("/api/leads?email=special", headers=auth_headers)
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["last_name"] == "Emailer"


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


async def test_create_lead_minimal(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.post(
        "/api/leads",
        json={"last_name": "Minimal", "company": "MinimalCo"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["last_name"] == "Minimal"
    assert data["status"] == "New"  # default
    assert data["company"] == "MinimalCo"


async def test_create_lead_with_all_fields(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    payload = {
        "first_name": "Full",
        "last_name": "Lead",
        "email": "full.lead@example.com",
        "phone": "+1-555-0300",
        "company": "FullLeadCo",
        "title": "VP Sales",
        "status": "Contacted",
        "lead_source": "Web",
        "industry": "Finance",
    }
    resp = await client.post("/api/leads", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "Contacted"
    assert data["lead_source"] == "Web"
    assert data["industry"] == "Finance"


async def test_create_lead_requires_last_name(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.post("/api/leads", json={"company": "NoCo"}, headers=auth_headers)
    assert resp.status_code == 422


async def test_create_lead_requires_company(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.post("/api/leads", json={"last_name": "NoCompany"}, headers=auth_headers)
    assert resp.status_code == 422


async def test_create_lead_sets_created_by(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    lead = await _create_lead(client, auth_headers)
    assert lead["created_by_id"] is not None


# ---------------------------------------------------------------------------
# Get by ID
# ---------------------------------------------------------------------------


async def test_get_lead_by_id(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    lead = await _create_lead(client, auth_headers, last_name="Fetch", company="FetchCo")
    resp = await client.get(f"/api/leads/{lead['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == lead["id"]
    assert resp.json()["last_name"] == "Fetch"


async def test_get_lead_not_found(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.get("/api/leads/999999999", headers=auth_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


async def test_update_lead_status(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    lead = await _create_lead(client, auth_headers, status="New")
    resp = await client.patch(f"/api/leads/{lead['id']}", json={"status": "Qualified"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "Qualified"


async def test_update_lead_partial_preserves_fields(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    lead = await _create_lead(client, auth_headers, last_name="Preserve", company="KeepMe", status="New")
    resp = await client.patch(f"/api/leads/{lead['id']}", json={"industry": "Retail"}, headers=auth_headers)
    data = resp.json()
    assert data["company"] == "KeepMe"
    assert data["status"] == "New"
    assert data["industry"] == "Retail"


async def test_update_lead_not_found(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.patch("/api/leads/999999999", json={"status": "Qualified"}, headers=auth_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Soft delete
# ---------------------------------------------------------------------------


async def test_soft_delete_lead(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    lead = await _create_lead(client, auth_headers)
    resp = await client.delete(f"/api/leads/{lead['id']}", headers=auth_headers)
    assert resp.status_code == 204


async def test_deleted_lead_returns_404(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    lead = await _create_lead(client, auth_headers)
    await client.delete(f"/api/leads/{lead['id']}", headers=auth_headers)
    resp = await client.get(f"/api/leads/{lead['id']}", headers=auth_headers)
    assert resp.status_code == 404


async def test_deleted_lead_excluded_from_list(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    lead = await _create_lead(client, auth_headers)
    await client.delete(f"/api/leads/{lead['id']}", headers=auth_headers)
    resp = await client.get("/api/leads", headers=auth_headers)
    ids = [item["id"] for item in resp.json()["items"]]
    assert lead["id"] not in ids


async def test_delete_lead_not_found(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.delete("/api/leads/999999999", headers=auth_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Auth requirement
# ---------------------------------------------------------------------------


async def test_leads_require_auth_list(client: AsyncClient) -> None:
    resp = await client.get("/api/leads")
    assert resp.status_code == 401


async def test_leads_require_auth_create(client: AsyncClient) -> None:
    resp = await client.post("/api/leads", json={"last_name": "Unauth", "company": "Co"})
    assert resp.status_code == 401

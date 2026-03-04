"""Tests for Opportunity CRUD endpoints.

Covers: list/paginate/filter, create (minimal/full/validation/auto-probability/audit),
get by id/404, update (stage change triggers is_won/is_closed), soft delete,
pipeline endpoint, and auth requirements.
"""

from datetime import date, timedelta

from httpx import AsyncClient

from tests.helpers import create_account, create_opportunity

_TODAY = date.today().isoformat()
_NEXT_MONTH = (date.today() + timedelta(days=30)).isoformat()
_NEXT_QUARTER = (date.today() + timedelta(days=90)).isoformat()


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


async def test_list_opportunities_empty(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.get("/api/opportunities", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


async def test_list_opportunities_returns_created(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    await create_opportunity(client, auth_headers, name="Big Deal")
    resp = await client.get("/api/opportunities", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Big Deal"


async def test_list_opportunities_pagination(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    for i in range(5):
        await create_opportunity(client, auth_headers, name=f"Deal {i}")
    resp = await client.get("/api/opportunities?limit=2&offset=0", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5


async def test_list_filter_by_stage(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    await create_opportunity(client, auth_headers, name="Qualified", stage="Qualification")
    await create_opportunity(client, auth_headers, name="Prospecting Deal")
    resp = await client.get("/api/opportunities?stage=Qualification", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Qualified"


async def test_list_filter_by_account(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    account = await create_account(client, auth_headers, name="Target Account")
    await create_opportunity(client, auth_headers, name="Deal A", account_id=account["id"])
    await create_opportunity(client, auth_headers, name="Deal B")
    resp = await client.get(f"/api/opportunities?account_id={account['id']}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Deal A"


async def test_list_filter_by_close_date_range(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    await create_opportunity(client, auth_headers, name="Soon", close_date=_TODAY)
    await create_opportunity(client, auth_headers, name="Later", close_date=_NEXT_QUARTER)
    resp = await client.get(
        f"/api/opportunities?close_date_from={_TODAY}&close_date_to={_NEXT_MONTH}",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Soon"


async def test_list_filter_by_is_closed(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    await create_opportunity(client, auth_headers, name="Won", stage="Closed Won")
    await create_opportunity(client, auth_headers, name="Open")
    resp = await client.get("/api/opportunities?is_closed=false", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    # Only open records
    assert all(not item["is_closed"] for item in data["items"])


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


async def test_create_opportunity_minimal(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.post(
        "/api/opportunities",
        json={"name": "Min Deal", "close_date": _TODAY},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Min Deal"
    assert data["stage"] == "Prospecting"
    assert data["is_won"] is False
    assert data["is_closed"] is False


async def test_create_opportunity_full(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    account = await create_account(client, auth_headers)
    payload = {
        "name": "Full Deal",
        "account_id": account["id"],
        "stage": "Qualification",
        "amount": "50000.00",
        "close_date": _NEXT_MONTH,
        "lead_source": "Web",
        "description": "Big opportunity",
    }
    resp = await client.post("/api/opportunities", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["stage"] == "Qualification"
    assert data["account_id"] == account["id"]
    assert data["lead_source"] == "Web"


async def test_create_auto_probability_from_stage(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.post(
        "/api/opportunities",
        json={"name": "Value Prop Deal", "stage": "Value Proposition", "close_date": _TODAY},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["probability"] == 50  # DEFAULT_STAGE_PROBABILITIES["Value Proposition"]


async def test_create_manual_probability_overrides_default(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.post(
        "/api/opportunities",
        json={"name": "Custom Prob", "stage": "Prospecting", "close_date": _TODAY, "probability": 35},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["probability"] == 35


async def test_create_invalid_probability(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.post(
        "/api/opportunities",
        json={"name": "Bad Prob", "close_date": _TODAY, "probability": 150},
        headers=auth_headers,
    )
    assert resp.status_code == 422


async def test_create_invalid_stage(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.post(
        "/api/opportunities",
        json={"name": "Bad Stage", "close_date": _TODAY, "stage": "InvalidStage"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


async def test_create_sets_audit_fields(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.post(
        "/api/opportunities",
        json={"name": "Audit Deal", "close_date": _TODAY},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["created_by_id"] is not None
    assert data["owner_id"] is not None


async def test_create_closed_won_sets_flags(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.post(
        "/api/opportunities",
        json={"name": "Won Deal", "stage": "Closed Won", "close_date": _TODAY},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["is_won"] is True
    assert data["is_closed"] is True


async def test_create_closed_lost_sets_flags(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.post(
        "/api/opportunities",
        json={"name": "Lost Deal", "stage": "Closed Lost", "close_date": _TODAY},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["is_won"] is False
    assert data["is_closed"] is True


async def test_create_requires_close_date(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.post("/api/opportunities", json={"name": "No Date"}, headers=auth_headers)
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Get by ID
# ---------------------------------------------------------------------------


async def test_get_opportunity_by_id(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    opp = await create_opportunity(client, auth_headers, name="Fetch Me")
    resp = await client.get(f"/api/opportunities/{opp['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == opp["id"]
    assert resp.json()["name"] == "Fetch Me"


async def test_get_opportunity_not_found(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.get("/api/opportunities/999999999", headers=auth_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


async def test_update_opportunity_name(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    opp = await create_opportunity(client, auth_headers, name="Old Name")
    resp = await client.patch(f"/api/opportunities/{opp['id']}", json={"name": "New Name"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


async def test_update_stage_changes_is_won(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    opp = await create_opportunity(client, auth_headers)
    resp = await client.patch(f"/api/opportunities/{opp['id']}", json={"stage": "Closed Won"}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_won"] is True
    assert data["is_closed"] is True


async def test_update_stage_closed_lost(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    opp = await create_opportunity(client, auth_headers)
    resp = await client.patch(f"/api/opportunities/{opp['id']}", json={"stage": "Closed Lost"}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_won"] is False
    assert data["is_closed"] is True


async def test_update_auto_probability_on_stage_change(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    opp = await create_opportunity(client, auth_headers, stage="Prospecting")
    resp = await client.patch(
        f"/api/opportunities/{opp['id']}", json={"stage": "Negotiation/Review"}, headers=auth_headers
    )
    assert resp.status_code == 200
    assert resp.json()["probability"] == 90


async def test_update_opportunity_not_found(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.patch("/api/opportunities/999999999", json={"name": "Ghost"}, headers=auth_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Soft delete
# ---------------------------------------------------------------------------


async def test_soft_delete_opportunity(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    opp = await create_opportunity(client, auth_headers)
    resp = await client.delete(f"/api/opportunities/{opp['id']}", headers=auth_headers)
    assert resp.status_code == 204


async def test_deleted_opportunity_returns_404(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    opp = await create_opportunity(client, auth_headers)
    await client.delete(f"/api/opportunities/{opp['id']}", headers=auth_headers)
    resp = await client.get(f"/api/opportunities/{opp['id']}", headers=auth_headers)
    assert resp.status_code == 404


async def test_deleted_excluded_from_list(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    opp = await create_opportunity(client, auth_headers, name="Gone")
    await client.delete(f"/api/opportunities/{opp['id']}", headers=auth_headers)
    resp = await client.get("/api/opportunities", headers=auth_headers)
    ids = [item["id"] for item in resp.json()["items"]]
    assert opp["id"] not in ids


async def test_delete_not_found(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.delete("/api/opportunities/999999999", headers=auth_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Pipeline endpoint
# ---------------------------------------------------------------------------


async def test_pipeline_returns_stage_groupings(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    await create_opportunity(client, auth_headers, stage="Prospecting", amount="10000")
    await create_opportunity(client, auth_headers, stage="Prospecting", amount="20000")
    await create_opportunity(client, auth_headers, stage="Qualification", amount="50000")
    resp = await client.get("/api/opportunities/pipeline", headers=auth_headers)
    assert resp.status_code == 200
    pipeline = resp.json()
    assert isinstance(pipeline, list)
    stages = {item["stage"] for item in pipeline}
    assert "Prospecting" in stages
    assert "Qualification" in stages
    prospecting = next(item for item in pipeline if item["stage"] == "Prospecting")
    assert prospecting["count"] == 2
    assert float(prospecting["total_amount"]) == 30000.0


# ---------------------------------------------------------------------------
# Auth requirements
# ---------------------------------------------------------------------------


async def test_opportunities_require_auth_list(client: AsyncClient) -> None:
    resp = await client.get("/api/opportunities")
    assert resp.status_code == 401


async def test_opportunities_require_auth_create(client: AsyncClient) -> None:
    resp = await client.post("/api/opportunities", json={"name": "Unauth", "close_date": _TODAY})
    assert resp.status_code == 401

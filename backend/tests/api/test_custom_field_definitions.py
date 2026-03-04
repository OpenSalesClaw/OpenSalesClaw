"""Tests for CustomFieldDefinition CRUD + custom field validation.

Covers: CRUD of definitions, type validation, required field enforcement,
picklist value validation, definitions scoped by object_name, and integration
with Account create/update (custom field validation).
"""

from httpx import AsyncClient

from tests.helpers import create_account


async def _create_definition(client: AsyncClient, headers: dict[str, str], **kwargs) -> dict:
    """Helper: create a custom field definition (requires superuser headers)."""
    payload = {
        "object_name": "accounts",
        "field_name": "test_field",
        "field_type": "text",
        **kwargs,
    }
    resp = await client.post("/api/custom-field-definitions", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


async def test_list_definitions_empty(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.get("/api/custom-field-definitions", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


async def test_list_definitions_filter_by_object_name(
    client: AsyncClient, auth_headers: dict[str, str], superuser_headers: dict[str, str]
) -> None:
    await _create_definition(client, superuser_headers, object_name="accounts", field_name="acct_custom")
    await _create_definition(client, superuser_headers, object_name="contacts", field_name="cont_custom")
    resp = await client.get("/api/custom-field-definitions?object_name=accounts", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["object_name"] == "accounts"


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


async def test_create_definition_text(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    resp = await client.post(
        "/api/custom-field-definitions",
        json={"object_name": "accounts", "field_name": "industry_code", "field_type": "text"},
        headers=superuser_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["field_type"] == "text"
    assert data["field_name"] == "industry_code"


async def test_create_definition_picklist_valid(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    resp = await client.post(
        "/api/custom-field-definitions",
        json={
            "object_name": "leads",
            "field_name": "tier",
            "field_type": "picklist",
            "picklist_values": ["Gold", "Silver", "Bronze"],
        },
        headers=superuser_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["picklist_values"] == ["Gold", "Silver", "Bronze"]


async def test_create_definition_picklist_empty_values_fails(
    client: AsyncClient, superuser_headers: dict[str, str]
) -> None:
    resp = await client.post(
        "/api/custom-field-definitions",
        json={
            "object_name": "leads",
            "field_name": "bad_picklist",
            "field_type": "picklist",
            "picklist_values": [],
        },
        headers=superuser_headers,
    )
    assert resp.status_code == 422


async def test_create_definition_picklist_missing_values_fails(
    client: AsyncClient, superuser_headers: dict[str, str]
) -> None:
    resp = await client.post(
        "/api/custom-field-definitions",
        json={
            "object_name": "leads",
            "field_name": "no_values_picklist",
            "field_type": "picklist",
        },
        headers=superuser_headers,
    )
    assert resp.status_code == 422


async def test_create_definition_requires_superuser(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.post(
        "/api/custom-field-definitions",
        json={"object_name": "accounts", "field_name": "blocked", "field_type": "text"},
        headers=auth_headers,
    )
    assert resp.status_code == 403


async def test_create_definition_requires_auth(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/custom-field-definitions",
        json={"object_name": "accounts", "field_name": "noauth", "field_type": "text"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Get by ID
# ---------------------------------------------------------------------------


async def test_get_definition_by_id(
    client: AsyncClient, auth_headers: dict[str, str], superuser_headers: dict[str, str]
) -> None:
    defn = await _create_definition(client, superuser_headers, field_name="get_me_field")
    resp = await client.get(f"/api/custom-field-definitions/{defn['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == defn["id"]


async def test_get_definition_not_found(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.get("/api/custom-field-definitions/999999999", headers=auth_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


async def test_update_definition(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    defn = await _create_definition(client, superuser_headers, field_name="update_me", field_label="Old label")
    resp = await client.patch(
        f"/api/custom-field-definitions/{defn['id']}",
        json={"field_label": "New Label", "is_required": True},
        headers=superuser_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["field_label"] == "New Label"
    assert data["is_required"] is True


# ---------------------------------------------------------------------------
# Soft delete
# ---------------------------------------------------------------------------


async def test_soft_delete_definition(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    defn = await _create_definition(client, superuser_headers, field_name="delete_me_field")
    resp = await client.delete(f"/api/custom-field-definitions/{defn['id']}", headers=superuser_headers)
    assert resp.status_code == 204


async def test_deleted_definition_returns_404(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    defn = await _create_definition(client, superuser_headers, field_name="gone_field")
    await client.delete(f"/api/custom-field-definitions/{defn['id']}", headers=superuser_headers)
    resp = await client.get(f"/api/custom-field-definitions/{defn['id']}", headers=superuser_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Custom field validation in Account CRUD (integration tests)
# ---------------------------------------------------------------------------


async def test_account_accepts_valid_text_custom_field(
    client: AsyncClient, auth_headers: dict[str, str], superuser_headers: dict[str, str]
) -> None:
    await _create_definition(
        client, superuser_headers, object_name="accounts", field_name="crm_tier", field_type="text"
    )
    resp = await client.post(
        "/api/accounts",
        json={"name": "Custom Field Corp", "custom_fields": {"crm_tier": "Gold"}},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["custom_fields"]["crm_tier"] == "Gold"


async def test_account_rejects_wrong_type_custom_field(
    client: AsyncClient, auth_headers: dict[str, str], superuser_headers: dict[str, str]
) -> None:
    await _create_definition(client, superuser_headers, object_name="accounts", field_name="score", field_type="number")
    resp = await client.post(
        "/api/accounts",
        json={"name": "Bad Type Corp", "custom_fields": {"score": "not-a-number"}},
        headers=auth_headers,
    )
    assert resp.status_code == 422


async def test_account_rejects_unknown_custom_field(
    client: AsyncClient, auth_headers: dict[str, str], superuser_headers: dict[str, str]
) -> None:
    await _create_definition(
        client, superuser_headers, object_name="accounts", field_name="known_field", field_type="text"
    )
    resp = await client.post(
        "/api/accounts",
        json={"name": "Unknown Field Corp", "custom_fields": {"unknown_field": "oops"}},
        headers=auth_headers,
    )
    assert resp.status_code == 422


async def test_account_rejects_missing_required_custom_field(
    client: AsyncClient, auth_headers: dict[str, str], superuser_headers: dict[str, str]
) -> None:
    await _create_definition(
        client,
        superuser_headers,
        object_name="accounts",
        field_name="required_field",
        field_type="text",
        is_required=True,
    )
    resp = await client.post(
        "/api/accounts",
        json={"name": "Missing Required Corp", "custom_fields": {}},
        headers=auth_headers,
    )
    assert resp.status_code == 422


async def test_account_rejects_invalid_picklist_value(
    client: AsyncClient, auth_headers: dict[str, str], superuser_headers: dict[str, str]
) -> None:
    await client.post(
        "/api/custom-field-definitions",
        json={
            "object_name": "accounts",
            "field_name": "tier_pick",
            "field_type": "picklist",
            "picklist_values": ["Gold", "Silver"],
        },
        headers=superuser_headers,
    )
    resp = await client.post(
        "/api/accounts",
        json={"name": "Bad Picklist Corp", "custom_fields": {"tier_pick": "Platinum"}},
        headers=auth_headers,
    )
    assert resp.status_code == 422


async def test_account_update_validates_custom_fields(
    client: AsyncClient, auth_headers: dict[str, str], superuser_headers: dict[str, str]
) -> None:
    await _create_definition(
        client, superuser_headers, object_name="accounts", field_name="update_field", field_type="boolean"
    )
    account = await create_account(client, auth_headers)
    resp = await client.patch(
        f"/api/accounts/{account['id']}",
        json={"custom_fields": {"update_field": "not-a-bool"}},
        headers=auth_headers,
    )
    assert resp.status_code == 422

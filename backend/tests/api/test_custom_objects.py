"""Tests for Custom Object and Custom Object Record CRUD.

Covers: definition CRUD (superuser only), record CRUD, soft delete, field
validation via custom_field_definitions, permission checks.
"""

from httpx import AsyncClient

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _create_object(client: AsyncClient, headers: dict[str, str], **kwargs) -> dict:
    payload = {
        "api_name": "test_project",
        "label": "Project",
        "plural_label": "Projects",
        **kwargs,
    }
    resp = await client.post("/api/custom-objects", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


async def _create_record(client: AsyncClient, headers: dict[str, str], api_name: str, **kwargs) -> dict:
    payload: dict = {}
    payload.update(kwargs)
    resp = await client.post(f"/api/custom-objects/{api_name}/records", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# Custom Object Definition — List
# ---------------------------------------------------------------------------


async def test_list_custom_objects_empty(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.get("/api/custom-objects", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


# ---------------------------------------------------------------------------
# Custom Object Definition — Create
# ---------------------------------------------------------------------------


async def test_create_custom_object_requires_superuser(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.post(
        "/api/custom-objects",
        json={"api_name": "test", "label": "Test", "plural_label": "Tests"},
        headers=auth_headers,
    )
    assert resp.status_code == 403


async def test_create_custom_object_success(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    obj = await _create_object(client, superuser_headers)
    assert obj["api_name"] == "test_project"
    assert obj["label"] == "Project"
    assert obj["plural_label"] == "Projects"
    assert obj["is_active"] is True


async def test_create_custom_object_invalid_api_name(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    resp = await client.post(
        "/api/custom-objects",
        json={"api_name": "Invalid Name!", "label": "Test", "plural_label": "Tests"},
        headers=superuser_headers,
    )
    assert resp.status_code == 422


async def test_create_custom_object_duplicate_api_name(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    await _create_object(client, superuser_headers, api_name="unique_obj")
    resp = await client.post(
        "/api/custom-objects",
        json={"api_name": "unique_obj", "label": "Dup", "plural_label": "Dups"},
        headers=superuser_headers,
    )
    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# Custom Object Definition — Read / Update / Delete
# ---------------------------------------------------------------------------


async def test_get_custom_object(client: AsyncClient, superuser_headers: dict[str, str], auth_headers: dict) -> None:
    await _create_object(client, superuser_headers, api_name="get_test")
    resp = await client.get("/api/custom-objects/get_test", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["api_name"] == "get_test"


async def test_get_custom_object_not_found(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.get("/api/custom-objects/nonexistent_xyz", headers=auth_headers)
    assert resp.status_code == 404


async def test_update_custom_object(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    await _create_object(client, superuser_headers, api_name="upd_test")
    resp = await client.patch(
        "/api/custom-objects/upd_test",
        json={"label": "Updated Label", "is_active": False},
        headers=superuser_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["label"] == "Updated Label"
    assert data["is_active"] is False


async def test_delete_custom_object(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    await _create_object(client, superuser_headers, api_name="del_test")
    resp = await client.delete("/api/custom-objects/del_test", headers=superuser_headers)
    assert resp.status_code == 204
    # Subsequent GET should 404
    resp = await client.get("/api/custom-objects/del_test", headers=superuser_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Custom Object Records — CRUD
# ---------------------------------------------------------------------------


async def test_create_record(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    await _create_object(client, superuser_headers, api_name="rec_obj")
    record = await _create_record(client, superuser_headers, "rec_obj", name="My Record", data={"foo": "bar"})
    assert record["name"] == "My Record"
    assert record["data"] == {"foo": "bar"}
    assert record["custom_object_id"] is not None


async def test_list_records_empty(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    await _create_object(client, superuser_headers, api_name="empty_obj")
    resp = await client.get("/api/custom-objects/empty_obj/records", headers=superuser_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


async def test_list_records_with_name_filter(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    await _create_object(client, superuser_headers, api_name="filter_obj")
    await _create_record(client, superuser_headers, "filter_obj", name="Alpha")
    await _create_record(client, superuser_headers, "filter_obj", name="Beta")
    resp = await client.get("/api/custom-objects/filter_obj/records?name=alph", headers=superuser_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Alpha"


async def test_get_record(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    await _create_object(client, superuser_headers, api_name="gget_obj")
    record = await _create_record(client, superuser_headers, "gget_obj", name="GetMe")
    resp = await client.get(f"/api/custom-objects/gget_obj/records/{record['id']}", headers=superuser_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "GetMe"


async def test_update_record(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    await _create_object(client, superuser_headers, api_name="upd_obj")
    record = await _create_record(client, superuser_headers, "upd_obj", name="Before")
    resp = await client.patch(
        f"/api/custom-objects/upd_obj/records/{record['id']}",
        json={"name": "After", "data": {"key": "value"}},
        headers=superuser_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "After"
    assert data["data"] == {"key": "value"}


async def test_delete_record(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    await _create_object(client, superuser_headers, api_name="del_rec_obj")
    record = await _create_record(client, superuser_headers, "del_rec_obj", name="ToDelete")
    resp = await client.delete(f"/api/custom-objects/del_rec_obj/records/{record['id']}", headers=superuser_headers)
    assert resp.status_code == 204
    resp = await client.get(f"/api/custom-objects/del_rec_obj/records/{record['id']}", headers=superuser_headers)
    assert resp.status_code == 404


async def test_record_wrong_object(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    """A record ID from object A should 404 when fetched via object B's route."""
    await _create_object(client, superuser_headers, api_name="obj_a")
    await _create_object(client, superuser_headers, api_name="obj_b")
    record = await _create_record(client, superuser_headers, "obj_a", name="A Record")
    resp = await client.get(f"/api/custom-objects/obj_b/records/{record['id']}", headers=superuser_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Record data validation via CustomFieldDefinitions
# ---------------------------------------------------------------------------


async def test_record_data_validated_against_definitions(
    client: AsyncClient, superuser_headers: dict[str, str]
) -> None:
    """When a custom field definition exists for a custom object, record data is validated."""
    obj = await _create_object(client, superuser_headers, api_name="validated_obj")
    obj_id = obj["id"]

    # Create a required number field for this object
    await client.post(
        "/api/custom-field-definitions",
        json={
            "object_name": f"custom_object_{obj_id}",
            "field_name": "priority",
            "field_type": "number",
            "is_required": True,
        },
        headers=superuser_headers,
    )

    # Creating a record without the required field should fail
    resp = await client.post(
        "/api/custom-objects/validated_obj/records",
        json={"name": "Missing priority", "data": {}},
        headers=superuser_headers,
    )
    assert resp.status_code == 422

    # Creating with a valid value should succeed
    resp = await client.post(
        "/api/custom-objects/validated_obj/records",
        json={"name": "With priority", "data": {"priority": 5}},
        headers=superuser_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["priority"] == 5

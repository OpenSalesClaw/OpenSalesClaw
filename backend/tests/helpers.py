"""Shared test helpers for creating records via the API."""

from httpx import AsyncClient


async def create_account(client: AsyncClient, headers: dict[str, str], **kwargs) -> dict:
    """Create an account via the API and return the response JSON."""
    payload = {"name": "Test Account", **kwargs}
    resp = await client.post("/api/accounts", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


async def create_contact(client: AsyncClient, headers: dict[str, str], **kwargs) -> dict:
    """Create a contact via the API and return the response JSON."""
    payload = {"last_name": "Doe", **kwargs}
    resp = await client.post("/api/contacts", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


async def create_lead(client: AsyncClient, headers: dict[str, str], **kwargs) -> dict:
    """Create a lead via the API and return the response JSON."""
    payload = {"last_name": "Doe", "company": "Test Corp", **kwargs}
    resp = await client.post("/api/leads", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


async def create_opportunity(client: AsyncClient, headers: dict[str, str], **kwargs) -> dict:
    """Create an opportunity via the API and return the response JSON."""
    from datetime import date

    payload = {"name": "Test Opportunity", "close_date": date.today().isoformat(), **kwargs}
    resp = await client.post("/api/opportunities", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


async def create_case(client: AsyncClient, headers: dict[str, str], **kwargs) -> dict:
    """Create a case via the API and return the response JSON."""
    payload = {"subject": "Test Case", **kwargs}
    resp = await client.post("/api/cases", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


async def create_role(client: AsyncClient, headers: dict[str, str], **kwargs) -> dict:
    """Create a role via the API (requires superuser headers) and return the response JSON."""
    payload = {"name": "Test Role", **kwargs}
    resp = await client.post("/api/roles", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()

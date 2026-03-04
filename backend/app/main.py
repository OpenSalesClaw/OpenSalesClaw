import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import accounts, auth, cases, contacts, custom_field_definitions, leads, opportunities, roles, users
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.exceptions import register_exception_handlers
from app.seed import ensure_default_user, seed_demo_data

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG001
    """Run startup tasks (seeding) before the app begins serving requests."""
    async with AsyncSessionLocal() as session:
        try:
            admin = await ensure_default_user(session)
            await seed_demo_data(session, admin)
            await session.commit()
        except Exception:
            await session.rollback()
            logger.exception("Seeding failed — the application will still start.")
    yield


_DESCRIPTION = """
**OpenSalesClaw** is an open-source, self-hostable CRM platform modelled after Salesforce.

## Features

* Standard CRM objects: **Accounts, Contacts, Leads, Opportunities, Cases**
* Full **CRUD** with soft-delete, pagination, filtering, and sorting
* **Custom fields** backed by PostgreSQL JSONB with runtime type validation
* **Role-based access control** (RBAC) with user and role management
* OAuth 2.0 / JWT authentication

## Authentication

All endpoints (except `/api/auth/login`) require a Bearer token obtained from `/api/auth/login`.
"""

_TAGS_METADATA: list[dict] = [
    {"name": "auth", "description": "Authentication – obtain and refresh JWT tokens."},
    {"name": "accounts", "description": "Company or organisation records."},
    {"name": "contacts", "description": "Individual people associated with accounts."},
    {"name": "leads", "description": "Unqualified prospects not yet linked to an account."},
    {"name": "opportunities", "description": "Potential deals / sales in progress."},
    {"name": "cases", "description": "Customer support tickets and issues."},
    {"name": "users", "description": "User administration (superuser only)."},
    {"name": "roles", "description": "Role management with hierarchical permissions."},
    {"name": "custom-field-definitions", "description": "Define custom fields on any object."},
    {"name": "health", "description": "Health-check endpoint."},
]

app = FastAPI(
    title=settings.app_name,
    description=_DESCRIPTION,
    version="0.1.0",
    openapi_tags=_TAGS_METADATA,
    contact={"name": "OpenSalesClaw", "url": "https://github.com/opensalesclaw/opensalesclaw"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

register_exception_handlers(app)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(contacts.router)
app.include_router(leads.router)
app.include_router(opportunities.router)
app.include_router(cases.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(custom_field_definitions.router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/api/health", tags=["health"])
async def health() -> dict[str, Any]:
    """Returns a simple health-check response."""
    return {"status": "ok", "app": settings.app_name}

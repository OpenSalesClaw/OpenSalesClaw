import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import accounts, auth, contacts, leads
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


app = FastAPI(
    title=settings.app_name,
    description="Open-source self-hostable CRM platform",
    version="0.1.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
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


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/api/health", tags=["health"])
async def health() -> dict:
    """Returns a simple health-check response."""
    return {"status": "ok", "app": settings.app_name}

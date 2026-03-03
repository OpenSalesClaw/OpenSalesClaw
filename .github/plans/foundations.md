# Technical Foundations Plan

**Status:** Phase 4 Complete
**Created:** 2026-03-03

---

## Overview

Stand up the full-stack skeleton: PostgreSQL schema with 5 core tables (users, accounts, contacts, leads, custom_field_definitions), a FastAPI backend with JWT auth and CRUD for all entities, a React + Vite + TypeScript frontend shell, Docker Compose for local development, and a GitHub Actions CI pipeline. Every layer follows the conventions in `.github/copilot-instructions.md`.

**Goal:** A working vertical slice — login, create an account, list contacts — that proves the architecture and makes onboarding trivial (`docker compose up`).

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| **JWT auth** over Keycloak | Simplest foundation; add OAuth 2.0 / OIDC later when multi-tenant or SSO is needed |
| **Core 4 entities** (Users, Accounts, Contacts, Leads) | Enough to prove every architectural pattern (CRUD, relationships, picklist fields, soft deletes, pagination, custom fields) without overreach |
| **`pyproject.toml` + `uv`** | Modern, fast, lockfile support, aligns with Python ecosystem direction |
| **`custom_field_definitions` table from day one** | Extensibility backbone — validating custom fields requires the metadata table immediately |
| **Traefik in dev** | Keeps Docker Compose close to production topology (single entry point, path-based routing) while remaining zero-config |
| **Offset/limit pagination** | Simpler to implement, sufficient for CRM datasets; migrate to cursor-based later if needed |
| **No Opportunities, Cases, Campaigns yet** | Same CRUD pattern — once 4 entities work, adding more is mechanical with no new architectural questions |

---

## Phases

### Phase 1 — Project Scaffolding & Configuration

- [x] **1.1** Create the full directory tree:
  - `backend/app/{api,models,schemas,services,core}/` with `__init__.py` files
  - `backend/alembic/`
  - `backend/tests/{api,services}/`
  - `frontend/src/{components,pages,api}/`
  - `schema/`
  - `design/`
  - `entities/`

- [x] **1.2** Create `backend/pyproject.toml` with `uv` as package manager
  - Dependencies: `fastapi`, `uvicorn[standard]`, `sqlalchemy[asyncio]`, `asyncpg`, `alembic`, `pydantic[email]`, `pydantic-settings`, `python-jose[cryptography]`, `passlib[bcrypt]`, `python-multipart`, `httpx`
  - Dev dependencies: `pytest`, `pytest-asyncio`, `pytest-cov`, `ruff`, `mypy`

- [x] **1.3** Initialize `frontend/` via Vite + React + TypeScript scaffold
  - Dependencies: `react`, `react-dom`, `react-router-dom`, `zustand`, `axios`
  - Dev dependencies: `typescript`, `@types/react`, `@types/react-dom`, `vite`, `@vitejs/plugin-react`, `eslint`, `prettier`

- [x] **1.4** Create `.env.example` with all expected environment variables:
  - `DATABASE_URL`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `CORS_ORIGINS`
  - `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`

---

### Phase 2 — Database Schema

- [x] **2.1** Create `schema/schema.sql` with a reusable `set_updated_at()` trigger function that auto-sets `updated_at = NOW()` on every update, attached to all tables.

- [x] **2.2** **`users`** table:
  - `id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY`
  - `sfid VARCHAR(40)`
  - `email VARCHAR(255) NOT NULL UNIQUE`, `hashed_password VARCHAR(255) NOT NULL`
  - `first_name VARCHAR(100)`, `last_name VARCHAR(100)`
  - `is_active BOOLEAN DEFAULT TRUE`, `is_superuser BOOLEAN DEFAULT FALSE`
  - Standard columns: `custom_fields`, `owner_id`, `created_by_id`, `updated_by_id`, `created_at`, `updated_at`, `is_deleted`, `deleted_at`, `deleted_by_id`
  - Index on `email`

- [x] **2.3** **`accounts`** table:
  - `name VARCHAR(255) NOT NULL`
  - `type VARCHAR(50)` — picklist: Customer, Partner, Prospect, Vendor, Other
  - `industry VARCHAR(100)`, `website VARCHAR(255)`, `phone VARCHAR(40)`
  - `billing_street`, `billing_city`, `billing_state`, `billing_postal_code`, `billing_country`
  - `description TEXT`, `annual_revenue NUMERIC(18,2)`, `number_of_employees INTEGER`
  - Standard columns
  - Indexes on `name`, `owner_id`

- [x] **2.4** **`contacts`** table:
  - `account_id BIGINT REFERENCES accounts(id)`
  - `first_name VARCHAR(100)`, `last_name VARCHAR(100) NOT NULL`
  - `email VARCHAR(255)`, `phone VARCHAR(40)`, `mobile_phone VARCHAR(40)`
  - `title VARCHAR(128)`, `department VARCHAR(100)`
  - `mailing_street`, `mailing_city`, `mailing_state`, `mailing_postal_code`, `mailing_country`
  - Standard columns
  - Indexes on `account_id`, `email`, `last_name`

- [x] **2.5** **`leads`** table:
  - `first_name VARCHAR(100)`, `last_name VARCHAR(100) NOT NULL`
  - `email VARCHAR(255)`, `phone VARCHAR(40)`, `company VARCHAR(255) NOT NULL`
  - `title VARCHAR(128)`, `status VARCHAR(50) NOT NULL DEFAULT 'New'` — New, Contacted, Qualified, Unqualified, Converted
  - `lead_source VARCHAR(100)`, `industry VARCHAR(100)`
  - `converted_at TIMESTAMPTZ`, `converted_account_id BIGINT`, `converted_contact_id BIGINT`
  - Standard columns
  - Indexes on `email`, `status`, `company`

- [x] **2.6** **`custom_field_definitions`** table:
  - `object_name VARCHAR(100) NOT NULL` (e.g., `'accounts'`, `'contacts'`)
  - `field_name VARCHAR(100) NOT NULL`, `field_label VARCHAR(255)`
  - `field_type VARCHAR(50) NOT NULL` — Text, Number, Date, DateTime, Boolean, Picklist, MultiPicklist, Email, URL, TextArea, Currency
  - `is_required BOOLEAN DEFAULT FALSE`, `default_value TEXT`
  - `picklist_values JSONB`, `field_order INTEGER`, `description TEXT`
  - Standard columns
  - Unique constraint on `(object_name, field_name)`

---

### Phase 3 — Backend Core

- [x] **3.1** `backend/app/core/config.py` — `Settings` class using `pydantic-settings` `BaseSettings`:
  - `database_url: str`
  - `secret_key: str`
  - `access_token_expire_minutes: int = 30`
  - `cors_origins: list[str]`
  - `app_name: str = "OpenSalesClaw"`

- [x] **3.2** `backend/app/core/database.py` — async SQLAlchemy engine (`create_async_engine`) + `async_sessionmaker`. Provide `async def get_db()` dependency yielding `AsyncSession`.

- [x] **3.3** `backend/app/models/base.py` — `Base` declarative base + `StandardColumns` mixin providing all shared columns (`sfid`, `custom_fields`, `owner_id`, `created_by_id`, `updated_by_id`, `created_at`, `updated_at`, `is_deleted`, `deleted_at`, `deleted_by_id`). Every entity model inherits from both.

- [x] **3.4** `backend/app/core/security.py` — password hashing (passlib bcrypt), JWT token creation/verification (python-jose):
  - `create_access_token(subject: str) → str`
  - `verify_password(plain, hashed) → bool`
  - `hash_password(plain) → str`

- [x] **3.5** `backend/app/core/dependencies.py`:
  - `get_current_user` — extract JWT from `Authorization: Bearer`, decode, fetch user, raise 401 if invalid
  - `get_current_active_user` — also check `is_active`

- [x] **3.6** `backend/app/core/exceptions.py` — domain exceptions: `NotFoundError`, `ForbiddenError`, `ConflictError`, `ValidationError`. Register FastAPI exception handlers via `register_exception_handlers(app)`.

- [x] **3.7** `backend/app/core/pagination.py`:
  - `PaginationParams` dependency (offset/limit, defaults 0/20, max 200)
  - `PaginatedResponse[T]` generic schema: `items: list[T]`, `total: int`, `offset: int`, `limit: int`

---

### Phase 4 — Entity Implementation

For each entity, follow the pattern: **Model → Schemas → Service → Routes**.

- [x] **4.1** **Users**
  - Model: `backend/app/models/user.py` — `email`, `hashed_password`, `first_name`, `last_name`, `is_active`, `is_superuser` + standard columns
  - Schemas: `backend/app/schemas/user.py` — `UserCreate` (email, password, first_name, last_name), `UserUpdate`, `UserRead` (excludes hashed_password)
  - Service: `backend/app/services/user.py` — `create_user()`, `get_user_by_email()`, `get_user_by_id()`, `authenticate_user()`
  - Routes: `backend/app/api/auth.py` — `POST /api/auth/register`, `POST /api/auth/login` (returns JWT), `GET /api/auth/me`

- [x] **4.2** **Accounts**
  - Model, Schemas, Service, Routes in respective directories
  - Full CRUD: `GET /api/accounts` (paginated; filters: name, type, industry), `GET /api/accounts/{id}`, `POST /api/accounts`, `PATCH /api/accounts/{id}`, `DELETE /api/accounts/{id}` (soft delete)
  - Relationship: `contacts` (one-to-many)

- [x] **4.3** **Contacts**
  - Same CRUD pattern
  - Relationship: `account` (many-to-one)
  - Filters: `account_id`, `last_name`, `email`

- [x] **4.4** **Leads**
  - Same CRUD pattern
  - No FK relationships to other CRM entities (leads are standalone until converted)
  - Filters: `status`, `company`, `email`

- [x] **4.5** `backend/app/main.py` — FastAPI app instantiation:
  - Include all routers
  - Register exception handlers
  - Add CORS middleware
  - Health check: `GET /api/health`

---

### Phase 5 — Alembic Migrations

- [ ] **5.1** Initialize Alembic in `backend/alembic/` with async configuration pointing at `DATABASE_URL`. Configure `env.py` to import `Base.metadata` from models for autogenerate.

- [ ] **5.2** Generate initial migration creating all 5 tables + the `set_updated_at` trigger.

---

### Phase 6 — Testing Infrastructure

- [ ] **6.1** `backend/tests/conftest.py` — fixtures for:
  - Async test client (`httpx.AsyncClient`)
  - Test database (separate DB or transactional rollback)
  - Authenticated user fixture (pre-creates user, returns headers with valid JWT)

- [ ] **6.2** `backend/tests/api/test_auth.py` — test register, login, me, invalid credentials.

- [ ] **6.3** `backend/tests/api/test_accounts.py` — test list (empty), create, get by ID, update, soft delete, 404 on deleted, pagination.

- [ ] **6.4** `backend/tests/api/test_contacts.py` — same patterns + account relationship.

- [ ] **6.5** `backend/tests/api/test_leads.py` — same patterns + status filtering.

- [ ] **6.6** `backend/tests/services/test_user.py` — unit tests for user service (create, authenticate, duplicate email).

---

### Phase 7 — Frontend Shell

- [ ] **7.1** Initialize Vite + React + TypeScript project in `frontend/` with strict TypeScript config.

- [ ] **7.2** `frontend/src/api/client.ts` — Axios instance:
  - Base URL from env var
  - Automatic `Authorization` header injection from stored token
  - Response interceptor: 401 → redirect to login

- [ ] **7.3** `frontend/src/stores/authStore.ts` — Zustand store:
  - State: `token`, `user`, `isAuthenticated`
  - Actions: `login()`, `logout()`
  - Persist token in `localStorage`

- [ ] **7.4** `frontend/src/pages/LoginPage.tsx` — email + password form → call login endpoint → store token → redirect to dashboard.

- [ ] **7.5** `frontend/src/pages/DashboardPage.tsx` — placeholder authenticated page.

- [ ] **7.6** `frontend/src/pages/AccountsPage.tsx` — fetch + display paginated accounts table. "New Account" button with simple create form.

- [ ] **7.7** `frontend/src/App.tsx` — React Router:
  - Routes: `/login`, `/` (dashboard), `/accounts`, `/contacts`, `/leads`
  - `ProtectedRoute` component wrapping authenticated routes

- [ ] **7.8** `frontend/src/components/Layout.tsx` — sidebar nav (Accounts, Contacts, Leads) + top bar (user info, logout). Minimal but functional.

---

### Phase 8 — Docker & Local Development

- [ ] **8.1** `backend/Dockerfile` — multi-stage build:
  - Builder: `uv sync` dependencies
  - Runtime: copy app, run `uvicorn app.main:app`
  - Expose port 8000

- [ ] **8.2** `frontend/Dockerfile` — multi-stage build:
  - Builder: `npm install` + `npm run build`
  - Runtime: serve with nginx
  - Expose port 80

- [ ] **8.3** `docker-compose.yml` — 4 services:
  - **db**: `postgres:16-alpine`, data volume, health check
  - **backend**: builds from `backend/`, depends on `db`, environment from `.env`, port 8000
  - **frontend**: builds from `frontend/`, port 3000
  - **traefik**: `traefik:v3`, dashboard enabled for dev, routes `/api/*` → backend, `/*` → frontend

- [ ] **8.4** `docker-compose.override.yml` — dev overrides:
  - Mount source as volumes
  - `uvicorn --reload` for backend
  - `npm run dev` for frontend
  - Expose database port 5432

---

### Phase 9 — CI/CD Pipeline

- [ ] **9.1** `.github/workflows/ci.yml`:
  - **Lint job**: `ruff check` + `ruff format --check` + `mypy` (backend); `eslint` + `tsc --noEmit` (frontend)
  - **Test backend job**: PostgreSQL service container, `pytest --cov` with coverage threshold (80%)
  - **Test frontend job**: `tsc --noEmit` (add Vitest later)
  - **Build job**: `docker compose build` to verify images compile

---

## Verification Checklist

After all phases are complete, the following must work:

- [ ] `docker compose up -d` → all services healthy
- [ ] `curl http://localhost:8000/api/health` → 200 OK
- [ ] Register user → login → get token → `GET /api/auth/me` returns user
- [ ] Create account → list accounts → update → soft-delete → confirm excluded from list
- [ ] Create contact linked to account → list with filter
- [ ] Create lead → filter by status
- [ ] Frontend: login page → authenticate → dashboard → navigate to accounts → create one
- [ ] `cd backend && uv run pytest` → all tests pass
- [ ] Push to branch → GitHub Actions CI green (lint + test + build)

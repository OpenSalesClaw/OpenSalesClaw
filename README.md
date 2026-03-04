<p align="center">
  <h1 align="center">OpenSalesClaw</h1>
  <p align="center">
    The open-source CRM platform — a modern, self-hostable alternative to Salesforce.
  </p>
  <p align="center">
    <a href="#features">Features</a> · <a href="#tech-stack">Tech Stack</a> · <a href="#getting-started">Getting Started</a> · <a href="#architecture">Architecture</a> · <a href="#roadmap">Roadmap</a> · <a href="#contributing">Contributing</a>
  </p>
  <p align="center">
    <a href="https://github.com/YOUR_ORG/OpenSalesClaw/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="License"></a>
    <img src="https://img.shields.io/badge/status-early%20development-orange" alt="Status">
  </p>
</p>

---

## Why OpenSalesClaw?

Salesforce is powerful — but it's also expensive, opaque, and locked down. OpenSalesClaw is building a CRM that gives teams the same core capabilities without the vendor lock-in:

- **Self-hosted & open source** — deploy on your own infrastructure, own your data.
- **Familiar data model** — Accounts, Contacts, Leads, Opportunities, Cases, and more, modeled after real-world CRM patterns.
- **Extensible by design** — add custom objects and fields at runtime, no migrations required.
- **API-first** — every feature is accessible through a documented REST API.

---

## Features

### Pre-built CRM Objects

All the standard CRM entities you'd expect, with typed columns, relationships, and indexes out of the box:

| Core | Sales | Marketing | Activity |
|------|-------|-----------|----------|
| Account | Product | Campaign | Task |
| Contact | Pricebook | CampaignMember | Event |
| Lead | Quote | EmailTemplate | Note |
| Opportunity | Order | | Attachment |
| Case | Contract | | |
| User / Role | | | |
| RecordType | | | |

### Custom Objects & Fields

Create your own objects and add custom fields to any entity — standard or custom — without schema migrations. Powered by PostgreSQL JSONB with GIN indexes for fast querying:

```
POST /api/custom-fields
{
  "object_type": "contact",
  "api_name": "preferred_language",
  "label": "Preferred Language",
  "field_type": "picklist",
  "picklist_values": ["English", "French", "Spanish"]
}
```

Custom field values are validated at the application layer using dynamically-generated Pydantic models, then stored in a JSONB column alongside the record's native fields.

### Additional Highlights

- **Picklist management** — centralized picklist definitions and values, shared across objects
- **Multi-currency support** — ISO 4217 currencies baked into the schema
- **Soft deletes** — every record supports `is_deleted`, `deleted_at`, and `deleted_by` for audit trails
- **Record types** — classify records within the same object (e.g., "Business Account" vs "Partner Account")
- **Role hierarchy** — self-referencing role tree for access control
- **Historical CRM ID columns** — `sfid` fields on every table for Salesforce sync and migration

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Database** | PostgreSQL 16 |
| **API** | FastAPI (Python 3.11+) |
| **ORM & Migrations** | SQLAlchemy 2.x + Alembic |
| **Validation** | Pydantic v2 |
| **API Docs** | OpenAPI (auto-generated) |
| **Auth** | OAuth 2.0 / JWT |
| **Frontend** | React 19 + Vite + TypeScript |
| **UI Components** | shadcn/ui (Radix UI + Tailwind CSS) |
| **State Management** | Zustand |
| **HTTP Client** | Axios |
| **Containerisation** | Docker & Docker Compose |
| **Reverse Proxy / SSL** | Traefik v3 |
| **CI/CD** | GitHub Actions |

---

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/YOUR_ORG/OpenSalesClaw.git
cd OpenSalesClaw

# Configure environment variables
cp .env.example .env
# Edit .env and set a strong SECRET_KEY

# Start the full stack (database, backend, frontend, Traefik)
# Migrations run automatically on backend startup via entrypoint.sh
docker compose up -d
```

| Service | URL |
|---------|-----|
| Frontend | `http://localhost` |
| API | `http://localhost/api` |
| Interactive API docs | `http://localhost/api/docs` |
| Traefik dashboard | `http://localhost:8080` |

### Local Development (without Docker)

```bash
# Backend (requires Python 3.11+ and uv)
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload

# Frontend (requires Node.js 18+)
cd frontend
npm install
npm run dev        # Vite dev server at http://localhost:5173
```

> **Note:** Set `CORS_ORIGINS=["http://localhost:5173"]` in your `.env` when running the frontend via Vite.

### Running CI locally

A `Makefile` at the repo root mirrors every step of the GitHub Actions pipeline so you can validate your changes before pushing.

**Prerequisites:** `uv`, Node.js 20+, Docker with the Compose plugin.

```bash
# Full pipeline — lint, test, build (same as CI)
make ci

# Individual stages
make lint              # ruff + mypy + eslint + tsc
make lint-backend      # ruff check, ruff format --check, mypy
make lint-frontend     # eslint, tsc --noEmit
make test              # pytest (with coverage) + tsc
make test-backend      # pytest --cov --cov-fail-under=80 (starts DB automatically)
make build             # docker compose build --no-cache
```

`make test-backend` automatically starts the `db` service via Docker Compose and creates an `opensalesclaw_test` database if it does not exist. It exports the same environment variables used in CI, so results are directly comparable.

Run `make help` to list all available targets.

---

## Seeding

### Default admin user

A default admin user is **always created automatically** on first startup. No manual step is required.

| Setting | Default | Environment variable |
|---------|---------|----------------------|
| Email | `admin@opensalesclaw.com` | `DEFAULT_ADMIN_EMAIL` |
| Password | `admin` | `DEFAULT_ADMIN_PASSWORD` |

The admin user is only created if no user with that email already exists — creation is **idempotent**.

### Demo CRM data

To populate the database with realistic demo records (~20 accounts, ~50 contacts, ~30 leads, ~15 opportunities, ~10 cases, ~5 roles) set `SEED_DEMO_DATA=true`. Demo data is also idempotent and will be skipped if it detects existing records.

```bash
# Docker Compose — set the variable and restart
SEED_DEMO_DATA=true docker compose up -d

# Local development — add to your .env file
echo "SEED_DEMO_DATA=true" >> .env
uv run uvicorn app.main:app --reload
```

> **Dev environment:** `docker-compose.override.yml` sets `SEED_DEMO_DATA=true` by default, so demo data is seeded automatically when running in development mode. Production (`docker-compose.yml`) defaults to `false`.

### Overriding admin credentials

Set environment variables before starting the backend:

```bash
DEFAULT_ADMIN_EMAIL=me@mycompany.com DEFAULT_ADMIN_PASSWORD=supersecret docker compose up -d
```

Or add them to your `.env` file:

```dotenv
DEFAULT_ADMIN_EMAIL=me@mycompany.com
DEFAULT_ADMIN_PASSWORD=supersecret
SEED_DEMO_DATA=true
```

---

## Architecture

### Database Design Principles

- **Relational first** — core entities are proper tables with typed columns, foreign keys, and indexes. Not a flat key-value store.
- **JSONB for extensibility** — every table includes a `custom_fields JSONB` column with a GIN index so tenants can add fields without DDL changes.
- **Surrogate keys** — `BIGINT GENERATED ALWAYS AS IDENTITY` primary keys for performance. Historical CRM IDs (e.g., Salesforce 18-char IDs) are stored in a separate `VARCHAR(40)` column for sync.
- **UTC timestamps** — all timestamps use `TIMESTAMP WITH TIME ZONE`, stored in UTC.
- **Consistent metadata** — every table carries `created_at`, `updated_at`, `created_by_id`, `updated_by_id`, `is_deleted`, `deleted_at`, `deleted_by_id`.

### Custom Field Flow

```
Define field  →  Metadata table (custom_field_definitions)
                       ↓
Write value   →  Validated by Pydantic model built from metadata
                       ↓
Store value   →  Merged into record's JSONB column (contacts.custom_fields)
                       ↓
Query value   →  PostgreSQL JSONB operators + GIN index
```

---

## Project Structure

```
├── .github/              # GitHub Actions workflows & Copilot config
├── design/               # Architecture decision records & design docs
├── salesforce/           # Salesforce object metadata (CSVs) used as reference
│   └── objects/core/
├── schema/
│   └── schema.sql        # Full PostgreSQL schema (tables, indexes, triggers)
├── backend/              # FastAPI application (Python 3.11+)
│   ├── app/
│   │   ├── api/          # Route handlers (accounts, contacts, leads, opportunities, cases, users, roles, auth, custom-field-definitions)
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   ├── services/     # Business logic layer
│   │   ├── core/         # Config, security, dependencies, exceptions
│   │   └── main.py       # FastAPI app entry point
│   ├── alembic/          # Database migrations
│   ├── tests/            # pytest test suite (API & service tests)
│   └── pyproject.toml
├── frontend/             # React 19 + Vite + TypeScript application
│   └── src/
│       ├── api/          # Axios API client
│       ├── components/   # Shared UI components
│       ├── pages/        # Route-level page components
│       └── stores/       # Zustand state stores
├── docker-compose.yml
├── Makefile              # Local CI runner (mirrors GitHub Actions)
├── .env.example
└── README.md
```

---

## Roadmap

OpenSalesClaw is in **early development**. Here's what's planned:

- [x] Core database schema (Accounts, Contacts, Leads, Opportunities, Cases, Users, Roles, CustomFieldDefinitions)
- [x] Custom fields architecture (JSONB + metadata table + type validation)
- [x] Alembic migration setup
- [x] FastAPI REST endpoints — Accounts, Contacts, Leads, Opportunities, Cases, Users, Roles
- [x] Custom Field Definitions API (runtime field registration per object)
- [x] Role-based access control (RBAC) — superuser guard + role hierarchy with cycle detection
- [x] OAuth 2.0 authentication & JWT-based authorization
- [x] React frontend — Dashboard, Login, Accounts, Contacts, Leads, Opportunities, Cases (list + detail + forms)
- [x] Tailwind CSS v4 + shadcn/ui component library
- [x] Docker Compose production setup with Traefik
- [x] pytest test suite — 208 tests, 87%+ coverage
- [x] CI/CD pipeline (GitHub Actions + local `make ci` runner)
- [ ] Lead conversion (lead → account + contact + opportunity)
- [ ] Sales objects (Products, Pricebooks, Quotes, Orders, Contracts)
- [ ] Marketing objects (Campaigns, Campaign Members, Email Templates)
- [ ] Activity objects (Tasks, Events, Notes, Attachments)
- [ ] Reports & Dashboards engine
- [ ] Import/export tooling (CSV, Salesforce migration)
- [ ] Webhook & event system
- [ ] Multi-tenant support

---

## Contributing

OpenSalesClaw is an open-source project and contributions are welcome! Whether it's a bug report, a feature request, documentation improvement, or a pull request — every bit helps.

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/my-feature`)
3. **Commit** your changes (`git commit -m 'Add my feature'`)
4. **Push** to the branch (`git push origin feature/my-feature`)
5. **Open** a Pull Request

Please open an issue first for larger changes so we can discuss the approach.

---

## License

OpenSalesClaw is licensed under the [Apache License 2.0](LICENSE).

```
Copyright 2024-2026 OpenSalesClaw Contributors

Licensed under the Apache License, Version 2.0.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
```

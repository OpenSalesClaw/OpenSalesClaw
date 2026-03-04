# Copilot Instructions — OpenSalesClaw

## Project Overview

OpenSalesClaw is an open-source, self-hostable CRM platform modeled after Salesforce. It provides standard CRM entities (Accounts, Contacts, Leads, Opportunities, Cases, etc.) with extensibility through custom objects and fields powered by PostgreSQL JSONB. The project is in early development.

---

## Tech Stack

| Layer             | Technology                  |
|-------------------|-----------------------------|
| Database          | PostgreSQL                  |
| API               | FastAPI (Python 3.11+)      |
| ORM & Migrations  | SQLAlchemy 2.x + Alembic    |
| Validation        | Pydantic v2                 |
| Auth              | OAuth 2.0                   |
| Frontend          | React + Vite + TypeScript   |
| UI Components     | shadcn/ui (Radix UI + Tailwind CSS) |
| Containers        | Docker & Docker Compose     |
| Reverse Proxy     | Traefik                     |
| CI/CD             | GitHub Actions              |

---

## Project Structure

```
├── .github/              # GitHub config, workflows, copilot instructions
├── design/               # Architecture decision records & design docs
├── entities/             # Entity/object definitions and metadata
├── salesforce/           # Salesforce object metadata (CSVs) as reference
│   └── objects/core/
├── schema/
│   └── schema.sql        # Full PostgreSQL schema
├── backend/              # FastAPI application (Python)
│   ├── app/
│   │   ├── api/          # Route handlers grouped by entity
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   ├── services/     # Business logic layer
│   │   ├── core/         # Config, security, dependencies
│   │   └── main.py       # FastAPI app entry point
│   ├── alembic/          # Database migrations
│   ├── tests/            # pytest test suite
│   └── requirements.txt
├── frontend/             # React + Vite application (TypeScript)
├── docker-compose.yml
└── README.md
```

---

## Database Conventions

Follow these rules for ALL database work (SQL, SQLAlchemy models, migrations):

### Primary Keys
- Use `BIGINT GENERATED ALWAYS AS IDENTITY` for all primary key columns.
- Column name: `id`.

### Historical CRM IDs
- Every table includes an `sfid VARCHAR(40)` column for Salesforce 18-char IDs (used for sync/migration).

### Timestamps
- All timestamps use `TIMESTAMP WITH TIME ZONE`, stored in UTC.
- Every table must include: `created_at`, `updated_at` (both default `NOW()`).

### Soft Deletes
- Every table must include: `is_deleted BOOLEAN DEFAULT FALSE`, `deleted_at TIMESTAMPTZ`, `deleted_by_id BIGINT`.

### Audit Columns
- Every table must include: `created_by_id BIGINT`, `updated_by_id BIGINT` (FK to `users.id`).

### Custom Fields
- Every entity table includes a `custom_fields JSONB DEFAULT '{}'::jsonb` column.
- Add a GIN index on the `custom_fields` column: `CREATE INDEX idx_<table>_custom_fields ON <table> USING GIN (custom_fields)`.

### Naming
- Table names: **plural**, **snake_case** (e.g., `accounts`, `campaign_members`).
- Column names: **singular**, **snake_case** (e.g., `first_name`, `account_id`).
- Foreign keys: `<referenced_table_singular>_id` (e.g., `account_id`, `contact_id`).
- Indexes: `idx_<table>_<column(s)>`.
- Unique constraints: `uq_<table>_<column(s)>`.

### Standard Column Template

When creating a new entity table, always include this boilerplate set of columns:

```sql
id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
sfid            VARCHAR(40),
-- ... entity-specific columns ...
custom_fields   JSONB DEFAULT '{}'::jsonb,
owner_id        BIGINT REFERENCES users(id),
created_by_id   BIGINT REFERENCES users(id),
updated_by_id   BIGINT REFERENCES users(id),
created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
is_deleted      BOOLEAN NOT NULL DEFAULT FALSE,
deleted_at      TIMESTAMPTZ,
deleted_by_id   BIGINT REFERENCES users(id)
```

---

## Python / Backend Conventions

### General
- Target **Python 3.11+**. Use modern syntax (type hints, `|` union types, `match` statements where appropriate).
- Use **async** route handlers and database sessions by default.
- Follow PEP 8. Line length limit: 120 characters.

### FastAPI Routes
- Group routes by entity in `app/api/<entity>.py` (e.g., `app/api/accounts.py`).
- Use an `APIRouter` per entity with a meaningful prefix and tag: `router = APIRouter(prefix="/api/accounts", tags=["accounts"])`.
- Standard CRUD endpoints per entity:
  - `GET    /api/<entities>`         — list with pagination, filtering, sorting
  - `GET    /api/<entities>/{id}`    — retrieve single record
  - `POST   /api/<entities>`         — create
  - `PATCH  /api/<entities>/{id}`    — partial update
  - `DELETE /api/<entities>/{id}`    — soft delete (set `is_deleted=True`)
- Return appropriate HTTP status codes: 200 (OK), 201 (Created), 204 (No Content for delete), 404 (Not Found), 422 (Validation Error).

### SQLAlchemy Models
- Place in `app/models/<entity>.py`.
- Use SQLAlchemy 2.x declarative style with `Mapped` and `mapped_column`.
- Every model must include the standard audit/metadata columns.
- Use a shared `BaseModel` mixin or base class for the standard columns.
- Relationships use `Mapped[...]` with `relationship()`.
- Example:

```python
class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # ... entity-specific columns
    custom_fields: Mapped[dict] = mapped_column(JSONB, default=dict)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, server_default=func.now())
    # ... remaining standard columns
```

### Pydantic Schemas
- Place in `app/schemas/<entity>.py`.
- Define at minimum: `<Entity>Create`, `<Entity>Update` (all fields optional), `<Entity>Read`.
- Use `model_config = ConfigDict(from_attributes=True)` for ORM compatibility.
- Validate custom field values through dynamically-generated Pydantic models based on `custom_field_definitions`.

### Services / Business Logic
- Place non-trivial logic in `app/services/<entity>.py`.
- Keep route handlers thin — they should validate input, call a service, and return output.
- Services accept a database session and return model instances or raise domain exceptions.

### Error Handling
- Define custom exception classes in `app/core/exceptions.py`.
- Use FastAPI exception handlers to map domain exceptions to HTTP responses.
- Never expose internal error details (tracebacks, SQL) in API responses.

### Dependencies
- Use FastAPI `Depends()` for database sessions, auth, and current user.
- Manage dependencies in `app/core/dependencies.py`.

---

## Testing Conventions

- Use **pytest** with **pytest-asyncio** for async tests.
- Place tests in `backend/tests/`, mirroring the app structure (e.g., `tests/api/test_accounts.py`).
- Use factory functions or **factory_boy** for test data.
- Each test should be independent; use database transactions that roll back after each test.
- Minimum test coverage targets: API routes, service functions, custom field validation.

---

## Frontend Conventions (React + TypeScript)

- Use **TypeScript strict mode**.
- Components in `frontend/src/components/`, pages in `frontend/src/pages/`.
- Use functional components with hooks only (no class components).
- API calls via a centralized API client (e.g., `frontend/src/api/client.ts`).
- Use **React Router** for routing.
- State management: React Context or Zustand (avoid Redux unless complexity warrants it).

### UI Components (shadcn/ui)

- Use **shadcn/ui** as the primary component library. It is built on **Radix UI** primitives and styled with **Tailwind CSS**.
- Add new components via the shadcn CLI: `npx shadcn@latest add <component>`.
- Installed components live in `frontend/src/components/ui/` — do not edit them directly; prefer wrapping them.
- Use Tailwind utility classes for layout and spacing; avoid writing custom CSS unless absolutely necessary.
- Follow the shadcn/ui theming system: customise design tokens in `frontend/src/index.css` (CSS variables) rather than overriding component styles inline.
- Prefer shadcn/ui primitives (`Button`, `Input`, `Dialog`, `Table`, `Select`, etc.) over custom or third-party equivalents.

---

## Git & Workflow Conventions

- Branch naming: `feature/<short-description>`, `fix/<short-description>`, `chore/<short-description>`.
- Commit messages: imperative mood, concise (`Add account list endpoint`, `Fix lead conversion logic`).
- PRs should reference an issue when one exists.
- Keep PRs focused — one feature or fix per PR.

---

## Key Domain Terminology

Use Salesforce-aligned terminology for CRM concepts:

| Term | Meaning |
|------|---------|
| Account | Company or organization |
| Contact | Individual person associated with an account |
| Lead | Unqualified prospect (not yet linked to account/contact) |
| Opportunity | Potential deal/sale in progress |
| Case | Customer support ticket or issue |
| Campaign | Marketing initiative |
| Record Type | Sub-classification within an object (e.g., "Partner Account") |
| Picklist | Dropdown/enum field with predefined values |
| Custom Field | User-defined field stored in JSONB |
| Custom Object | User-defined entity created at runtime |

---

## Common Patterns to Follow

1. **New entity checklist**: SQL table → SQLAlchemy model → Pydantic schemas → service layer → API routes → tests.
2. **Always soft-delete** — never issue `DELETE FROM`. Set `is_deleted = TRUE`, `deleted_at = NOW()`, `deleted_by_id = <user>`.
3. **Filter out deleted records by default** — all list/get queries must include `WHERE is_deleted = FALSE` unless explicitly requesting deleted records.
4. **Pagination** — use offset/limit with sensible defaults (limit=20, max=200). Return total count in response metadata.
5. **Custom fields** — validate against `custom_field_definitions` before writing. Store in the record's `custom_fields` JSONB column.
6. **Owner assignment** — most entity records have an `owner_id` referencing `users.id`.
7. **updated_at trigger** — use a PostgreSQL trigger or application-level logic to set `updated_at = NOW()` on every update.

---

## What NOT to Do

- Do not use auto-incrementing `SERIAL` — use `BIGINT GENERATED ALWAYS AS IDENTITY`.
- Do not use naive datetimes — always use `TIMESTAMPTZ` (UTC).
- Do not hard-delete records — use soft deletes.
- Do not put business logic in route handlers — delegate to services.
- Do not skip the `custom_fields` JSONB column on new entity tables.
- Do not create frontend-only features without a backing API endpoint.
- Do not store secrets in code — use environment variables.

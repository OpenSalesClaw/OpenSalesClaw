# OpenSalesClaw — MVP Implementation Plan

> Detailed phased plan to complete all 34 MVP features from FEATURES.md.
> Based on codebase audit as of March 4, 2026.

---

## Current State Summary

The MVP requires **34 features** across backend, frontend, database, and infrastructure. Of these, roughly **15 are already Done** (Accounts/Contacts/Leads CRUD, auth, Docker, migrations, pagination, base scaffolds, tests). The remaining **~19 features** group into 8 implementation phases.

Each phase follows the established entity checklist: SQL table → Alembic migration → SQLAlchemy model → Pydantic schemas → CRUDService → APIRouter → tests.

### What's Already Done

| Area | Details |
|------|---------|
| **Accounts CRUD** (F-CORE-001) | Model, schema, service, API, 18 tests |
| **Contacts CRUD** (F-CORE-002) | Model, schema, service, API, 19 tests |
| **Leads CRUD** (F-CORE-003) | Model, schema, service, API, 19 tests |
| **Auth** (F-SEC-002) | JWT login, register, `/api/auth/me`, 10 tests |
| **Users** (F-CORE-006) | Model + service + auth endpoints (partial — no admin API) |
| **CustomFieldDefinition** | ORM model exists (no schema/service/API/tests) |
| **Database** | 5 tables (users, accounts, contacts, leads, custom_field_definitions), `set_updated_at` triggers, GIN indexes on `custom_fields` |
| **Base Infrastructure** | `StandardColumns` mixin, generic `CRUDService`, `PaginatedResponse`, exception hierarchy, async sessions, pydantic-settings config |
| **Docker** (T-ARCH-003/004) | Dev + prod compose with Traefik, multi-stage Dockerfiles, Alembic in entrypoint |
| **Frontend Scaffold** (T-ARCH-002) | React 19 + Vite + TypeScript, Zustand auth store, Axios client, Layout with sidebar, LoginPage, AccountsPage (list + create). **Note:** Tailwind CSS + shadcn/ui are not yet installed — required before Phase 6. |
| **Tests** | ~86 backend tests, conftest with rollback isolation, `httpx.AsyncClient` |

---

## Phase 0 — FEATURES.md Status Reconciliation

Update FEATURES.md to reflect actual codebase state. The following items are listed as "Not Started" but are already implemented:

| ID | Feature | Actual Status |
|----|---------|---------------|
| T-ARCH-001 | FastAPI Scaffold | Done |
| T-ARCH-002 | React + Vite Scaffold | Done |
| T-ARCH-005 | Environment Configuration | Done |
| T-ARCH-012 | Health Checks | Done (`/api/health`) |
| T-DB-001 | PostgreSQL Schema Design | Done (5 tables) |
| T-DB-003 | BaseModel Mixin | Done (`StandardColumns`) |
| T-DB-004 | JSONB Custom Fields + GIN | Done (schema-level) |
| T-DB-009 | `updated_at` Trigger | Done (SQL trigger) |
| T-DB-010 | Soft-Delete Query Filter | Done (service-level) |
| T-SEC-002 | SQL Injection Prevention | Done (SQLAlchemy) |
| T-SEC-004 | Secrets Management | Done (.env + pydantic-settings) |
| T-PERF-001 | Async DB Sessions | Done |
| F-INT-001 | RESTful CRUD API | Done for 3 entities |
| F-UI-006 | Navigation / App Bar | Done (sidebar + top bar) |

---

## Phase 1 — Database: New Entity Tables + Migration

**Goal:** Add `opportunities`, `cases`, and `roles` tables to the schema and create an Alembic migration.

**Features covered:** Foundation for F-CORE-004, F-CORE-005, F-CORE-007

### Steps

1. **Add `roles` table** to `schema/schema.sql`:
   - `id` (BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY)
   - `sfid` (VARCHAR 40)
   - `name` (VARCHAR 255, NOT NULL, UNIQUE)
   - `parent_role_id` (BIGINT, self-referential FK to `roles.id`)
   - `description` (TEXT)
   - All standard columns (`custom_fields`, `owner_id`, `created_by_id`, `updated_by_id`, `created_at`, `updated_at`, `is_deleted`, `deleted_at`, `deleted_by_id`)
   - Index: `idx_roles_parent_role_id`
   - `set_updated_at` trigger

2. **Add `role_id` column** to the `users` table:
   - `role_id BIGINT REFERENCES roles(id)`

3. **Add `opportunities` table** to `schema/schema.sql`:
   - `id`, `sfid`
   - `name` (VARCHAR 255, NOT NULL)
   - `account_id` (BIGINT, FK to `accounts.id`)
   - `contact_id` (BIGINT, FK to `contacts.id`, nullable)
   - `stage` (VARCHAR 100, NOT NULL, DEFAULT `'Prospecting'`)
   - `probability` (INTEGER, CHECK 0–100)
   - `amount` (NUMERIC(18,2))
   - `close_date` (DATE, NOT NULL)
   - `type` (VARCHAR 100)
   - `lead_source` (VARCHAR 100)
   - `next_step` (VARCHAR 255)
   - `description` (TEXT)
   - `is_won` (BOOLEAN DEFAULT FALSE)
   - `is_closed` (BOOLEAN DEFAULT FALSE)
   - `closed_at` (TIMESTAMPTZ)
   - All standard columns
   - Indexes: `account_id`, `stage`, `close_date`, `owner_id`, GIN on `custom_fields`
   - `set_updated_at` trigger

4. **Add `cases` table** to `schema/schema.sql`:
   - `id`, `sfid`
   - `case_number` (VARCHAR 30, UNIQUE, auto-populated by application)
   - `account_id` (BIGINT, FK to `accounts.id`)
   - `contact_id` (BIGINT, FK to `contacts.id`)
   - `subject` (VARCHAR 255, NOT NULL)
   - `description` (TEXT)
   - `status` (VARCHAR 100, NOT NULL, DEFAULT `'New'`)
   - `priority` (VARCHAR 50, DEFAULT `'Medium'`)
   - `origin` (VARCHAR 100)
   - `type` (VARCHAR 100)
   - `reason` (VARCHAR 255)
   - `closed_at` (TIMESTAMPTZ)
   - All standard columns
   - Indexes: `account_id`, `contact_id`, `status`, `priority`, GIN on `custom_fields`
   - `set_updated_at` trigger

5. **Generate Alembic migration** in `backend/alembic/versions/`:
   - Name: `20260304_add_opportunities_cases_roles.py`
   - Follow pattern from `20260303_a8f3c2e1b4d0_initial_schema.py`
   - Include all new tables, indexes, triggers, and the `role_id` column addition to `users`

### Files Changed

| Action | File |
|--------|------|
| Modify | `schema/schema.sql` |
| Create | `backend/alembic/versions/20260304_*_add_opportunities_cases_roles.py` |

---

## Phase 2 — Opportunities CRUD (F-CORE-004 + F-SALES-001)

**Goal:** Full Opportunities entity following the established Account/Contact/Lead pattern.

**Features covered:** F-CORE-004, F-SALES-001

### Steps

1. **Create `backend/app/models/opportunity.py`:**
   - SQLAlchemy model inheriting `Base` + `StandardColumns`
   - Relationships to `Account` and `Contact` (many-to-one, noload)
   - Define `OPPORTUNITY_STAGES` constant:
     ```
     Prospecting, Qualification, Needs Analysis, Value Proposition,
     Id. Decision Makers, Perception Analysis, Proposal/Price Quote,
     Negotiation/Review, Closed Won, Closed Lost
     ```
   - Define `DEFAULT_STAGE_PROBABILITIES` dict mapping stage → probability %

2. **Export model** from `backend/app/models/__init__.py`

3. **Create `backend/app/schemas/opportunity.py`:**
   - `OpportunityCreate`: `name`, `account_id`, `stage`, `close_date` required; `amount`, `probability`, `type`, `lead_source`, `next_step`, `description`, `contact_id`, `custom_fields` optional
   - `OpportunityUpdate`: all fields optional
   - `OpportunityRead`: extends `StandardReadFields`
   - Validators: `probability` must be 0–100, `stage` from allowed list

4. **Export schemas** from `backend/app/schemas/__init__.py`

5. **Create `backend/app/services/opportunity.py`:**
   - Extends `CRUDService[Opportunity, OpportunityCreate, OpportunityUpdate]`
   - `apply_list_filters`: filter by `account_id`, `stage`, `is_closed`, `close_date_from`/`close_date_to` range
   - Override `create`: auto-set `is_won`/`is_closed` based on stage (Closed Won → both True; Closed Lost → is_closed=True, is_won=False); auto-set `probability` from defaults if not provided
   - Override `update`: same stage-driven logic when stage changes
   - Default sort: `close_date ASC`

6. **Create `backend/app/api/opportunities.py`:**
   - `APIRouter(prefix="/api/opportunities", tags=["opportunities"])`
   - Standard 5 CRUD endpoints (list, get, create, update, delete)
   - `GET /api/opportunities/pipeline`: return counts + sum of amounts grouped by stage

7. **Register router** in `backend/app/main.py`

8. **Create `backend/tests/api/test_opportunities.py`:**
   - ~20 tests: list/paginate/filter by stage/account/date range, create (min/full/validation/auto-probability/audit), get by id/404, update (stage change triggers is_won/is_closed), soft delete, pipeline endpoint, auth requirements

9. **Add `create_opportunity` helper** to `backend/tests/helpers.py`

### Files

| Action | File |
|--------|------|
| Create | `backend/app/models/opportunity.py` |
| Create | `backend/app/schemas/opportunity.py` |
| Create | `backend/app/services/opportunity.py` |
| Create | `backend/app/api/opportunities.py` |
| Create | `backend/tests/api/test_opportunities.py` |
| Modify | `backend/app/models/__init__.py` |
| Modify | `backend/app/schemas/__init__.py` |
| Modify | `backend/app/main.py` |
| Modify | `backend/tests/helpers.py` |

---

## Phase 3 — Cases CRUD (F-CORE-005)

**Goal:** Full Cases entity following the same pattern.

**Features covered:** F-CORE-005, F-SVC-001 (partial — lifecycle)

### Steps

1. **Create `backend/app/models/case.py`:**
   - Model with `StandardColumns`
   - `CASE_STATUSES`: New, Working, Escalated, Closed
   - `CASE_PRIORITIES`: Low, Medium, High, Critical
   - Relationships to `Account` and `Contact` (many-to-one, noload)

2. **Export** from `backend/app/models/__init__.py`

3. **Create `backend/app/schemas/case.py`:**
   - `CaseCreate`: `subject` required; `account_id`, `contact_id`, `description`, `status`, `priority`, `origin`, `type`, `reason`, `custom_fields` optional
   - `CaseUpdate`: all optional
   - `CaseRead`: extends `StandardReadFields`
   - Validators: `status` from allowed list, `priority` from allowed list

4. **Export** from `backend/app/schemas/__init__.py`

5. **Create `backend/app/services/case.py`:**
   - Extends `CRUDService`
   - `apply_list_filters`: `account_id`, `contact_id`, `status`, `priority`
   - Override `create`: auto-generate `case_number` (format `CS-{zero-padded sequential}` via DB query for max existing), auto-set `closed_at` when status is "Closed"
   - Override `update`: set `closed_at` when status changes to "Closed", clear it when reopened
   - Default sort: `created_at DESC`

6. **Create `backend/app/api/cases.py`:**
   - Standard CRUD at `/api/cases`

7. **Register router** in `backend/app/main.py`

8. **Create `backend/tests/api/test_cases.py`:**
   - ~18 tests: CRUD + filters + `case_number` auto-generation + status-driven `closed_at` + auth

9. **Add `create_case` helper** to `backend/tests/helpers.py`

### Files

| Action | File |
|--------|------|
| Create | `backend/app/models/case.py` |
| Create | `backend/app/schemas/case.py` |
| Create | `backend/app/services/case.py` |
| Create | `backend/app/api/cases.py` |
| Create | `backend/tests/api/test_cases.py` |
| Modify | `backend/app/models/__init__.py` |
| Modify | `backend/app/schemas/__init__.py` |
| Modify | `backend/app/main.py` |
| Modify | `backend/tests/helpers.py` |

---

## Phase 4 — Users Admin CRUD + Roles (F-CORE-006 + F-CORE-007)

**Goal:** Complete user management API and basic role hierarchy.

**Features covered:** F-CORE-006, F-CORE-007

### Steps

1. **Create `backend/app/models/role.py`:**
   - `Role` model: `name`, `parent_role_id` (self-referential FK), `description`, `StandardColumns`
   - `children` and `parent` relationships
   - `users` relationship (back-populates)

2. **Modify `backend/app/models/user.py`:**
   - Add `role_id` mapped_column with FK to `roles.id`
   - Add `role` relationship

3. **Export `Role`** from `backend/app/models/__init__.py`

4. **Create `backend/app/schemas/role.py`:**
   - `RoleCreate` (`name` required, `parent_role_id` optional, `description` optional)
   - `RoleUpdate` (all optional)
   - `RoleRead` (extends `StandardReadFields`, includes `parent_role_id`)

5. **Modify `backend/app/schemas/user.py`:**
   - Add `UserList` schema (without password hash)
   - Extend `UserUpdate` with `is_active`, `is_superuser`, `role_id` (admin fields)
   - Add `role_id` and nested `RoleRead` to `UserRead`

6. **Create `backend/app/services/role.py`:**
   - `CRUDService` subclass
   - `get_hierarchy()` method returning tree structure
   - Validate no circular parent references on create/update

7. **Refactor `backend/app/services/user.py`:**
   - Add `list_users(db, pagination, filters)` — paginated, filterable by `is_active`, `role_id`, email search
   - Add `deactivate_user(db, user_id)` — set `is_active=False`

8. **Create `backend/app/api/users.py`:**
   - `APIRouter(prefix="/api/users", tags=["users"])`
   - `GET /` — list users (admin-only)
   - `GET /{id}` — get user
   - `PATCH /{id}` — update user (admin-only)
   - `DELETE /{id}` — soft-deactivate (admin-only)
   - All require auth; write endpoints require `is_superuser`

9. **Create `backend/app/api/roles.py`:**
   - Full CRUD at `/api/roles`
   - Superuser-only for create/update/delete
   - `GET /api/roles/hierarchy` — tree view

10. **Register both routers** in `backend/app/main.py`

11. **Create tests:**
    - `backend/tests/api/test_users.py` — RBAC enforcement (non-admin gets 403), user list/filter, deactivation
    - `backend/tests/api/test_roles.py` — CRUD, hierarchy operations, circular reference prevention

### Files

| Action | File |
|--------|------|
| Create | `backend/app/models/role.py` |
| Create | `backend/app/schemas/role.py` |
| Create | `backend/app/services/role.py` |
| Create | `backend/app/api/users.py` |
| Create | `backend/app/api/roles.py` |
| Create | `backend/tests/api/test_users.py` |
| Create | `backend/tests/api/test_roles.py` |
| Modify | `backend/app/models/user.py` |
| Modify | `backend/app/models/__init__.py` |
| Modify | `backend/app/schemas/user.py` |
| Modify | `backend/app/schemas/__init__.py` |
| Modify | `backend/app/services/user.py` |
| Modify | `backend/app/main.py` |

---

## Phase 5 — Custom Fields System (F-CUST-001, F-CUST-002, F-CUST-004, F-CUST-005)

**Goal:** Turn the existing `CustomFieldDefinition` model into a functional metadata-driven custom field system.

**Features covered:** F-CUST-001, F-CUST-002, F-CUST-004, F-CUST-005

### Steps

1. **Create `backend/app/schemas/custom_field_definition.py`:**
   - `FieldType` enum: `text`, `number`, `date`, `datetime`, `boolean`, `picklist`, `email`, `url`, `phone`, `currency`, `percent`, `textarea`
   - `CustomFieldDefinitionCreate`: `object_name`, `field_name`, `field_label`, `field_type` required; `is_required`, `default_value`, `picklist_values`, `field_order`, `description` optional
   - `CustomFieldDefinitionUpdate`: all optional
   - `CustomFieldDefinitionRead`: extends `StandardReadFields`
   - Validator: `picklist_values` must be non-empty list when `field_type == 'picklist'`

2. **Create `backend/app/services/custom_field_definition.py`:**
   - `CRUDService` subclass
   - `apply_list_filters`: filter by `object_name`
   - `get_definitions_for_object(db, object_name)` → list of active definitions
   - `validate_custom_fields(db, object_name, custom_fields_dict)` class method:
     - Load definitions for object
     - Validate each field's type (text→str, number→int|float, boolean→bool, date→ISO date string, picklist→value in allowed list, email→email format, etc.)
     - Check required fields are present
     - Reject unknown field names not in definitions

3. **Create `backend/app/api/custom_field_definitions.py`:**
   - CRUD at `/api/custom-field-definitions`
   - `GET ?object_name=accounts` to list definitions per object
   - Superuser-only for create/update/delete

4. **Integrate validation into base service:**
   - Modify `CRUDService.create` and `CRUDService.update` in `backend/app/services/base.py`
   - When `custom_fields` is present in payload, call `validate_custom_fields` using the model's `__tablename__` as `object_name`
   - This gives all entities automatic custom field validation

5. **Update base schemas:**
   - Ensure `custom_fields` is typed as `dict[str, Any] | None` in Create/Update base schemas in `backend/app/schemas/base.py`

6. **Register router** in `backend/app/main.py`

7. **Create `backend/tests/api/test_custom_field_definitions.py`:**
   - CRUD tests for definitions
   - Type validation tests (create text definition → save text ✓, save integer ✗)
   - Required field enforcement
   - Picklist value validation
   - Definitions scoped by `object_name`

8. **Add integration tests** to existing entity test files:
   - Create a custom field definition for accounts
   - Verify account create/update validates custom fields against it

### Files

| Action | File |
|--------|------|
| Create | `backend/app/schemas/custom_field_definition.py` |
| Create | `backend/app/services/custom_field_definition.py` |
| Create | `backend/app/api/custom_field_definitions.py` |
| Create | `backend/tests/api/test_custom_field_definitions.py` |
| Modify | `backend/app/services/base.py` |
| Modify | `backend/app/schemas/base.py` |
| Modify | `backend/app/schemas/__init__.py` |
| Modify | `backend/app/main.py` |
| Modify | `backend/tests/api/test_accounts.py` (integration tests) |

---

## Phase 6 — Frontend: List Views, Detail Pages, Forms (F-UI-001, F-UI-002, F-UI-003)

**Goal:** Functional frontend for all 5 core entities with list, detail, and create/edit views.

**Features covered:** F-UI-001, F-UI-002, F-UI-003, F-UI-006

### Steps

1. **shadcn/ui setup** (prerequisite — do this first):
   - Install Tailwind CSS and its Vite plugin: `npm install tailwindcss @tailwindcss/vite`
   - Initialize shadcn/ui: `npx shadcn@latest init` (choose a base color, confirm `src/index.css` for CSS variables)
   - Install required shadcn/ui components: `npx shadcn@latest add button input table dialog form select badge toast`
   - Verify `frontend/src/components/ui/` is populated and `tailwind.config.ts` / `vite.config.ts` are updated

2. **Shared components** — Create reusable components in `frontend/src/components/`. Build on shadcn/ui primitives — do **not** hand-roll base UI elements:
   - `DataTable.tsx` — generic sortable, paginated table. Wrap the shadcn/ui `Table` primitive. Accepts column definitions (`{key, label, render?}`) and data array. Pagination controls use shadcn/ui `Button`.
   - `RecordForm.tsx` — generic form component. Wrap shadcn/ui `Form`, `Input`, `Select`, and `Textarea` primitives. Accepts field definitions and renders appropriate inputs (text, number, date, select/picklist, textarea, email, url, phone).
   - `DetailView.tsx` — generic read-only record view with field labels, values, and an edit `Button`.
   - `DeleteConfirmDialog.tsx` — confirmation modal built on the shadcn/ui `Dialog` primitive.
   - `FilterBar.tsx` — horizontal filter bar using shadcn/ui `Input`, `Select`, and `Button` components.

2. **API types & modules** — Create in `frontend/src/api/`:
   - `types.ts` — TypeScript interfaces for all entities matching Pydantic `Read` schemas + `PaginatedResponse<T>` generic
   - `accounts.ts`, `contacts.ts`, `leads.ts`, `opportunities.ts`, `cases.ts` — typed CRUD functions per entity

3. **Contacts pages:**
   - Implement `ContactsPage.tsx` — list with table (name, email, account, phone), create modal
   - Create `ContactDetailPage.tsx` — view/edit toggle
   - Route: `/contacts/:id`

4. **Leads pages:**
   - Implement `LeadsPage.tsx` — list with table (name, company, status, email, lead source), create modal
   - Create `LeadDetailPage.tsx` — view/edit toggle
   - Route: `/leads/:id`

5. **Opportunities pages:**
   - Create `OpportunitiesPage.tsx` — list with table (name, account, stage, amount, close date), create modal
   - Create `OpportunityDetailPage.tsx`
   - Routes: `/opportunities`, `/opportunities/:id`

6. **Cases pages:**
   - Create `CasesPage.tsx` — list with table (case number, subject, status, priority, account), create modal
   - Create `CaseDetailPage.tsx`
   - Routes: `/cases`, `/cases/:id`

7. **Accounts enhancement:**
   - Create `AccountDetailPage.tsx` — show account fields + related contacts, opportunities, cases as sub-tables
   - Route: `/accounts/:id`

8. **Update navigation:**
   - Add Opportunities and Cases to sidebar in `frontend/src/components/Layout.tsx`

9. **Update routing:**
   - Add all new routes to `frontend/src/App.tsx` inside `ProtectedRoute`

10. **Dashboard:**
    - Update `DashboardPage.tsx` to fetch real counts from API and display in stat cards
    - Optionally show pipeline summary if opportunities endpoint is available

### Files

| Action | File |
|--------|------|
| Create | `frontend/src/components/DataTable.tsx` |
| Create | `frontend/src/components/RecordForm.tsx` |
| Create | `frontend/src/components/DetailView.tsx` |
| Create | `frontend/src/components/DeleteConfirmDialog.tsx` |
| Create | `frontend/src/components/FilterBar.tsx` |
| Create | `frontend/src/api/types.ts` |
| Create | `frontend/src/api/accounts.ts` |
| Create | `frontend/src/api/contacts.ts` |
| Create | `frontend/src/api/leads.ts` |
| Create | `frontend/src/api/opportunities.ts` |
| Create | `frontend/src/api/cases.ts` |
| Create | `frontend/src/pages/ContactDetailPage.tsx` |
| Create | `frontend/src/pages/LeadDetailPage.tsx` |
| Create | `frontend/src/pages/OpportunitiesPage.tsx` |
| Create | `frontend/src/pages/OpportunityDetailPage.tsx` |
| Create | `frontend/src/pages/CasesPage.tsx` |
| Create | `frontend/src/pages/CaseDetailPage.tsx` |
| Create | `frontend/src/pages/AccountDetailPage.tsx` |
| Modify | `frontend/src/pages/ContactsPage.tsx` |
| Modify | `frontend/src/pages/LeadsPage.tsx` |
| Modify | `frontend/src/pages/DashboardPage.tsx` |
| Modify | `frontend/src/components/Layout.tsx` |
| Modify | `frontend/src/App.tsx` |

---

## Phase 7 — OpenAPI Docs + Timezone Handling (F-INT-002, F-I18N-004)

**Goal:** Polish API documentation and ensure correct timezone behavior.

**Features covered:** F-INT-002, F-I18N-004

### Steps

1. **OpenAPI configuration** in `backend/app/main.py`:
   - Set `docs_url="/docs"`, `redoc_url="/redoc"`, `openapi_url="/api/openapi.json"`
   - Add proper `title`, `description`, `version`, `contact`, `license_info`
   - Verify all endpoints have response model declarations
   - Ensure consistent tag grouping

2. **Timezone enforcement:**
   - Audit all Pydantic schemas — ensure datetime fields use timezone-aware `datetime`
   - Add `AfterValidator` in `backend/app/schemas/base.py` that rejects naive datetimes
   - Database already stores `TIMESTAMPTZ` — this is schema-level guard only

3. **Frontend timezone display:**
   - Ensure display layer converts UTC timestamps to user's local timezone
   - Use `Intl.DateTimeFormat` or format utility in shared component
   - All data stays UTC — display concern only

### Files

| Action | File |
|--------|------|
| Modify | `backend/app/main.py` |
| Modify | `backend/app/schemas/base.py` |
| Modify | Frontend date display components |

---

## Phase 8 — Quality & Completeness Pass

**Goal:** Tie up loose ends, validate the full MVP is functional.

### Steps

1. **Seed data update** — Extend `backend/app/seed.py`:
   - ~10 opportunities at various stages linked to seeded accounts
   - ~10 cases linked to seeded accounts/contacts
   - 2–3 roles (CEO, VP Sales, Sales Rep) with hierarchy

2. **Test coverage audit:**
   - Run `pytest --cov=app --cov-report=term-missing`
   - Identify and fill gaps
   - Target: >80% line coverage on `app/` code
   - Ensure every API endpoint has at least one happy-path and one error-path test

3. **Error response consistency:**
   - Verify all endpoints return consistent error shapes via the exception hierarchy
   - Add any missing error codes (e.g., 409 for duplicate custom field definitions)

4. **FEATURES.md update:**
   - Mark all completed MVP features as "Done"

5. **README update:**
   - Current entity list
   - API endpoints summary
   - Setup instructions (dev + production)
   - API usage examples

### Files

| Action | File |
|--------|------|
| Modify | `backend/app/seed.py` |
| Modify | `backend/tests/test_seed.py` |
| Modify | `FEATURES.md` |
| Modify | `README.md` |
| Modify | Various test files (gap-filling) |

---

## Dependency Order

```
Phase 1 (DB) ──► Phase 2 (Opportunities) ──► Phase 6 (Frontend)
            ├──► Phase 3 (Cases) ──────────►
            ├──► Phase 4 (Users + Roles) ──►
            └──► Phase 5 (Custom Fields) ──►
                                             Phase 7 (Docs + TZ)
                                             Phase 8 (Quality)
```

- **Phase 1** must complete first (all new tables)
- **Phases 2–5** can be parallelized after Phase 1
- **Phase 6** depends on Phases 2–4 (needs API endpoints to exist)
- **Phases 7–8** are sequential finalization after everything else

---

## Estimated Scope

| Phase | New Files | Modified Files | New Tests |
|-------|-----------|----------------|-----------|
| 0 | 0 | 1 | 0 |
| 1 | 1 migration | 1 (schema.sql) | 0 |
| 2 | 4 (model, schema, service, api) | 4 (inits, main, helpers) | ~20 |
| 3 | 4 | 4 | ~18 |
| 4 | 7 (role model/schema/service/api, user api, test files) | 5 | ~25 |
| 5 | 4 (schema, service, api, tests) | 4 (base service, base schema, init, main) | ~15 |
| 6 | ~18 (pages, components, api modules) | 4 (App.tsx, Layout, Dashboard, existing pages) | 0 (P1) |
| 7 | 0 | 3 | 0 |
| 8 | 0 | 5 (seed, README, FEATURES, tests) | ~10 |
| **Total** | **~38** | **~31** | **~88** |

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| **Defer full OAuth 2.0 / OIDC (F-SEC-001)** | Current JWT auth with username/password is sufficient for MVP. External IdP support moves to P1. |
| **Roles are informational for MVP** | Implement `roles` table and hierarchy, but defer full RBAC enforcement middleware (per-endpoint permission checks) to P1. MVP roles provide organizational context, not access control. |
| **Case auto-numbering via application** | Use application-level sequential numbering (`CS-00001`) rather than DB-generated, since the format requires string formatting. |
| **Continue inline styles for frontend** | Maintains velocity for MVP. CSS framework (Tailwind) introduced in P1 UI polish pass. |
| **Custom field validation in base service** | Integrate into `CRUDService` base class so all entities get automatic validation — no per-entity wiring needed. |
| **No frontend tests for MVP** | Frontend test framework (Vitest) deferred to P1. Focus testing budget on backend API coverage. |
| **No refresh tokens for MVP** | Single JWT access token flow. Refresh token mechanism added in P1 security hardening. |

---

## Verification Checklist

- [ ] `cd backend && pytest -v --cov=app --cov-report=term-missing` — all tests pass, >80% coverage
- [ ] `cd frontend && npm run build` — no TypeScript errors, builds successfully
- [ ] `docker compose up` — all services healthy
- [ ] Login → navigate to all entity pages → perform CRUD on each entity
- [ ] `/docs` shows all endpoints with request/response schemas
- [ ] Create custom field definition → create record with custom field → validation works
- [ ] Create Account → add Contact → create Opportunity → create Case → all appear in list views
- [ ] Account detail page shows related contacts, opportunities, and cases
- [ ] Pipeline endpoint returns correct stage groupings
- [ ] Seed data populates all entity types on fresh database

# Foundations Review — OpenSalesClaw

**Date:** 2026-03-04  
**Scope:** Full repository audit — schema, models, services, API, tests, frontend, infra, docs

---

## P0 — Bugs

### 1. `CustomFieldDefinition.id` uses `Integer` instead of `BigInteger`

**File:** [backend/app/models/custom_field_definition.py](backend/app/models/custom_field_definition.py#L14)

The model declares `id` as `Integer` with `autoincrement=True` while the SQL schema and migration both use `BIGINT GENERATED ALWAYS AS IDENTITY`. This produces a 32-bit `SERIAL` column when tests create tables from metadata, violating the project convention.

**Fix:** Change to `mapped_column(BigInteger, Identity(always=True), primary_key=True)` to match all other models and the migration.

---

### 2. Frontend env var name mismatch — API base URL is always `undefined`

| Location | Variable name |
|----------|---------------|
| [frontend/src/api/client.ts](frontend/src/api/client.ts#L3) | `VITE_API_URL` |
| [docker-compose.override.yml](docker-compose.override.yml#L42) | `VITE_API_BASE_URL` |

The names don't match. The frontend always reads `undefined` and falls back to `''`, which only works by accident when the Vite dev proxy is active.

**Fix:** Pick one name (recommend `VITE_API_BASE_URL`) and update `client.ts` to match.

---

## P1 — Correctness Issues

### 3. Lead model missing ForeignKeys on conversion columns

**File:** [backend/app/models/lead.py](backend/app/models/lead.py#L22-L23)

`converted_account_id` and `converted_contact_id` are plain `BigInteger` columns with no `ForeignKey(...)`. The SQL schema and migration both declare `REFERENCES accounts(id)` / `REFERENCES contacts(id)`. Tests using `Base.metadata.create_all` won't enforce referential integrity.

**Fix:** Add `ForeignKey("accounts.id")` and `ForeignKey("contacts.id")` to the mapped columns.

---

### 4. `sfid` column type mismatch — `Text` vs `String(40)`

**File:** [backend/app/models/base.py](backend/app/models/base.py#L28)

The `StandardColumns` mixin declares `sfid` as `Text` (unbounded). The SQL schema and migration both use `VARCHAR(40)`.

**Fix:** Change to `mapped_column(String(40), nullable=True)`.

---

### 5. `get_current_user` dependency uses raw SQL, returns `dict`

**File:** [backend/app/core/dependencies.py](backend/app/core/dependencies.py#L34-L38)

Uses `text("SELECT * FROM users ...")` instead of the SQLAlchemy ORM. Returns a raw dict, forcing all route handlers to type the current user as `dict[str, Any]` instead of `User`.

**Fix:** Rewrite to use `select(User).where(User.id == user_id, User.is_deleted == False)` and return a `User` model instance.

---

### 6. `authenticate_user` raises `NotFoundError` for auth failures

**File:** [backend/app/services/user.py](backend/app/services/user.py#L44-L47)

Authentication failures (invalid password, inactive account) raise `NotFoundError`, which is semantically incorrect and forces the auth route to catch and re-raise as `HTTPException(401)`.

**Fix:** Create an `AuthenticationError(AppError)` exception with `status_code=401` and raise it directly from the service.

---

### 7. Test schema diverges from production schema

**File:** [backend/tests/conftest.py](backend/tests/conftest.py#L69)

Tests create tables via `Base.metadata.create_all` instead of running the Alembic migration. This means:
- Missing FK constraints on lead conversion columns (issue #3)
- Different `id` column type for `custom_field_definitions` (issue #1)
- Different `sfid` column type (issue #4)
- Missing `set_updated_at()` PostgreSQL trigger

**Fix (short-term):** Fix the model definitions (issues #1, #3, #4) so model metadata matches the migration. For the trigger, either run the migration in tests or add application-level `updated_at` handling in the `StandardColumns` mixin (it already has `onupdate=func.now()`, which covers ORM updates).

---

### 8. Entity models don't declare `Identity(always=True)` on primary keys

**Files:** All models in [backend/app/models/](backend/app/models/)

All entity models use `mapped_column(BigInteger, primary_key=True)` without `Identity(always=True)`. The migration handles this correctly, but `create_all` in tests generates `BIGSERIAL` instead of `GENERATED ALWAYS AS IDENTITY`.

**Fix:** Add `Identity(always=True)` to the `id` column in the `StandardColumns` mixin or in each model.

---

### 9. Missing `.env.example`

The README instructs `cp .env.example .env` but no `.env.example` file exists in the repository.

**Fix:** Create `.env.example` with all required variables and safe defaults.

---

## P2 — Improvements

### 10. Inline `HTTPException` import in auth route

**File:** [backend/app/api/auth.py](backend/app/api/auth.py#L39)

`from fastapi import HTTPException` appears inside the `except` block instead of at the top of the file.

**Fix:** Move to top-level imports.

---

### 11. No custom field validation against definitions

The copilot instructions require validating `custom_fields` against `custom_field_definitions`. Currently, any dict is accepted as-is with no validation.

**Fix (later):** Implement a validator in the service layer that loads applicable `custom_field_definitions` and validates the incoming `custom_fields` dict before persisting.

---

### 12. Service layer boilerplate duplication

**Files:** [backend/app/services/account.py](backend/app/services/account.py), [backend/app/services/contact.py](backend/app/services/contact.py), [backend/app/services/lead.py](backend/app/services/lead.py)

All three services implement nearly identical `get_by_id`, `list_*`, `create_*`, `update_*`, `delete_*` functions. ~70% of the code is duplicated.

**Fix:** Extract a generic `CRUDService[ModelType]` base that handles standard operations. Entity-specific services inherit and override only what differs.

---

### 13. Pydantic schema boilerplate duplication

Audit fields (`owner_id`, `created_by_id`, `updated_by_id`, `created_at`, `updated_at`, `custom_fields`) are copied across every `*Read` schema.

**Fix:** Create a `StandardReadFields` mixin class and have all `*Read` schemas inherit from it.

---

### 14. `UserRead` schema omits `custom_fields` and `owner_id`

**File:** [backend/app/schemas/user.py](backend/app/schemas/user.py#L18-L28)

Unlike other `*Read` schemas, `UserRead` doesn't expose `custom_fields` or `owner_id`, breaking the standard pattern.

**Fix:** Add the missing fields.

---

### 15. No `sfid` in any Read schema

None of the `*Read` schemas expose `sfid`. Consumers performing Salesforce sync would need this field.

**Fix:** Add `sfid: str | None` to the `StandardReadFields` mixin or to each Read schema.

---

### 16. Account relationship `primaryjoin` uses bare `False`

**File:** [backend/app/models/account.py](backend/app/models/account.py#L39)

The string-based `primaryjoin` uses `Contact.is_deleted == False` (Python `False`). While SQLAlchemy handles this, using `Contact.is_deleted == false()` or `.is_(False)` would be cleaner.

**Fix:** Update to use `false()` SQL literal or switch to expression-based `primaryjoin`.

---

### 17. Naming convention mismatch in `Base` metadata

**File:** [backend/app/models/base.py](backend/app/models/base.py#L12-L18)

The model `naming_convention` defines index names as `ix_%(column_0_label)s` but the project convention (and the migration) uses `idx_<table>_<column>`.

**Fix:** Update naming convention to `"ix": "idx_%(table_name)s_%(column_0_label)s"`.

---

### 18. Test helpers duplicated across test files

**Files:** [backend/tests/api/test_accounts.py](backend/tests/api/test_accounts.py#L12-L16), [backend/tests/api/test_contacts.py](backend/tests/api/test_contacts.py#L14-L17)

`_create_account` appears in both files.

**Fix:** Move shared helpers to `tests/helpers.py` or use pytest fixtures in `conftest.py`.

---

### 19. No automated migration in Docker

Neither the Dockerfile nor `docker-compose.yml` runs `alembic upgrade head` on startup.

**Fix:** Add an entrypoint script that runs migrations before starting uvicorn.

---

### 20. No health check for backend container

The `db` service has a health check in `docker-compose.yml` but `backend` does not, despite having a `/api/health` endpoint.

**Fix:** Add `healthcheck` to the backend service using `curl` or `wget` against `/api/health`.

---

### 21. Dual token storage in frontend

**Files:** [frontend/src/stores/authStore.ts](frontend/src/stores/authStore.ts), [frontend/src/api/client.ts](frontend/src/api/client.ts#L14)

The token is stored in both Zustand (persisted to `localStorage` via `auth-storage`) and directly in `localStorage` under `access_token`. The Axios interceptor reads from `access_token`. If either gets out of sync, auth breaks silently.

**Fix:** Use a single source of truth. Either read from the Zustand store in the interceptor, or drop the Zustand persistence and use `localStorage` directly.

---

### 22. No `package-lock.json` for frontend

The frontend `Dockerfile` references `package-lock.json*` (optional). Without a lock file, `npm ci` will fail or produce inconsistent builds.

**Fix:** Commit a `package-lock.json` to the repo.

---

### 23. `vite.config.ts` proxy reads wrong env var type

**File:** [frontend/vite.config.ts](frontend/vite.config.ts#L9)

Uses `process.env.VITE_API_URL`. `VITE_*` vars are only available via `import.meta.env` on the client side. In the Vite config (Node context), it would need to be a regular env var or read via `dotenv`.

**Fix:** Use a non-prefixed env var (e.g., `API_URL`) for the proxy target, or use `loadEnv()` from Vite.

---

### 24. ContactsPage and LeadsPage are stubs

**Files:** [frontend/src/pages/ContactsPage.tsx](frontend/src/pages/ContactsPage.tsx), [frontend/src/pages/LeadsPage.tsx](frontend/src/pages/LeadsPage.tsx)

Both pages show placeholder text despite the backend APIs being fully implemented.

---

### 25. Default secret key and admin password

**File:** [backend/app/core/config.py](backend/app/core/config.py#L10)

`secret_key` defaults to `"change-me-in-production"` and `default_admin_password` defaults to `"admin"`. A misconfigured production deployment would be immediately compromised.

**Fix:** Fail loudly at startup if the secret key is the default value and `ENV != dev`.

---

## P3 — Nice-to-Have / Cleanup

### 26. `python-jose` is unmaintained

**File:** [backend/pyproject.toml](backend/pyproject.toml#L13)

No release since 2022. Consider migrating to `PyJWT` or `joserfc`.

---

### 27. README roadmap checkmarks are inaccurate

**File:** [README.md](README.md#L179-L202)

Claims checkmarks for Opportunities, Cases, Roles, RecordTypes, multi-currency — none of which exist in the codebase.

**Fix:** Update checkmarks to reflect actual state.

---

### 28. FEATURES.md shows all items as "Not Started"

**File:** [FEATURES.md](FEATURES.md)

Despite several MVP features being implemented (auth, CRUD for 3 entities, Docker, pagination), every row says "Not Started".

**Fix:** Update statuses.

---

### 29. Empty `design/` and `entities/` directories

README references `design/custom-tables-fields-architecture.md` which doesn't exist. Both directories are empty.

**Fix:** Either create the referenced documents or remove the references.

---

### 30. No User relationships defined in model

**File:** [backend/app/models/user.py](backend/app/models/user.py)

No relationships back to accounts, contacts, or leads for `owner_id`, `created_by_id` etc. Limits eager-loading.

**Fix:** Add `relationship()` definitions as needed.

---

### 31. No frontend test infrastructure

No Vitest, Jest, or Playwright configuration exists.

---

### 32. No CI/CD pipeline

No GitHub Actions workflow files. Listed as P1 in FEATURES.md.

---

### 33. No password complexity validation

**File:** [backend/app/schemas/user.py](backend/app/schemas/user.py#L8)

Any string is accepted as a password. No minimum length or complexity rules.

---

### 34. No CORS configuration for production

`CORS_ORIGINS` in docker-compose uses a JSON array string `["http://localhost:3000"]` as default. Works but is fragile.

---

### 35. No request logging or request ID correlation middleware

Mentioned as P1 in FEATURES.md, not implemented.

---

## Suggested Fix Order

1. **Quick wins (issues #1, #2, #4, #10, #17)** — simple one-line fixes, high correctness impact
2. **Model correctness (#3, #8)** — ensure test schema matches production
3. **Auth cleanup (#5, #6, #21, #25)** — fix `get_current_user`, auth errors, token storage
4. **Infra (#9, #19, #20, #22, #23)** — `.env.example`, Docker migration, health check, lock file
5. **DRY refactors (#12, #13, #14, #15, #18)** — reduce boilerplate
6. **Docs (#27, #28, #29)** — accurate roadmap and feature status
7. **Frontend (#24)** — implement ContactsPage/LeadsPage
8. **Security & testing (#26, #31, #32, #33)** — later priorities
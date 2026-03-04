# MVP Review — Simplification & Improvement Plan

> Review of all MVP features marked "Done" in OpenSalesClaw as of March 4, 2026.
> Focus: eliminate bugs, reduce duplication, fix inconsistencies. No over-engineering.

---

## Bugs (fix first)

### 1. Opportunity & Case `update` skip custom field validation

Both `OpportunityService.update` (backend/app/services/opportunity.py L66-82) and `CaseService.update` (backend/app/services/case.py L77-89) override the base `update` method but never call `_validate_custom_fields`. A PATCH with invalid custom fields bypasses validation entirely.

**Fix:** Add `await self._validate_custom_fields(db, updates)` in both methods before applying changes, matching what the base `CRUDService.update` does.

### 2. Case list silently ignores `order_by` parameter

`CaseService.list` (backend/app/services/case.py L54) always passes `order_by=self.model.created_at.desc()`, ignoring whatever the caller provides.

**Fix:** Use the same pattern as `ContactService.list` — `order_by = order_by if order_by is not None else self.model.created_at.desc()`.

### 3. Case number race condition

`_generate_case_number` (backend/app/services/case.py L16-27) reads max case number and increments. Concurrent requests can produce duplicates, causing an unhandled `IntegrityError` → 500 error.

**Fix:** Use a PostgreSQL sequence (`CREATE SEQUENCE case_number_seq`) and `nextval('case_number_seq')` instead of manual max+1.

### 4. Unhandled `IntegrityError` on unique constraint violations

Creating a Role with a duplicate name or a CustomFieldDefinition with a duplicate `(object_name, field_name)` raises a raw 500. Only User creation checks for duplicates.

**Fix:** Add a try/except around `db.flush()` in `CRUDService.create` (or in each affected service) that catches `IntegrityError` and raises `ConflictError`.

### 5. Frontend type mismatches cause data loss

- Contact: frontend uses `mobile`, backend expects `mobile_phone` → mobile data silently dropped on create/update.
- Lead: frontend shows `company` as optional, backend requires it → form submits empty company, gets 422 with no useful message.
- Lead: frontend shows `annual_revenue`, `rating`, `is_converted` which don't exist on the backend response → phantom UI fields.
- Opportunity: `closed_at` tracked by backend but not in `OpportunityRead` → data is computed but never exposed.

**Fix:** Regenerate frontend types from the actual backend schemas. Add `closed_at` to `OpportunityRead`. Fix field name `mobile` → `mobile_phone` in frontend.

---

## Inconsistencies (standardize)

### 6. User service doesn't use `CRUDService` base

Every other entity uses `CRUDService`. User service uses standalone functions, reimplements pagination/filtering, and uses `deactivate_user` (sets `is_active=False`) instead of soft-delete (`is_deleted=True`). This means:
- Deactivated users still appear in `GET /api/users` (every other entity's delete hides the record).
- No custom field validation on user create/update.

**Fix:** Refactor `UserService` to extend `CRUDService`. Keep the password-hashing override in `create`/`update`. Replace `deactivate_user` with proper soft-delete for consistency. If "deactivate" (login-disabled but visible) is a separate need, keep `is_active` but also support soft-delete for actual removal.

### 7. Duplicate `/me` endpoints

Both `/api/auth/me` and `/api/users/me` return the current user.

**Fix:** Remove one. Keep `/api/auth/me` (it's the auth context), remove `/api/users/me`.

### 8. `UserRead` and `UserList` are identical

`UserList` was meant as a lightweight schema but has the exact same fields as `UserRead`.

**Fix:** Either differentiate them (e.g., drop `custom_fields` and `sfid` from `UserList`) or remove `UserList` and use `UserRead` everywhere.

### 9. `StandardReadFields` missing `is_deleted` metadata

Backend `StandardReadFields` omits `is_deleted`, `deleted_at`, `deleted_by_id`. Frontend `StandardFields` type includes `is_deleted`. The frontend field will always be `undefined` at runtime.

**Fix:** Remove `is_deleted` from frontend `StandardFields` (API responses for active records never include it). If admin "view deleted records" is needed later, add a separate schema.

### 10. Login page and Layout ignore the design system

`LoginPage.tsx` and `Layout.tsx` use massive inline `React.CSSProperties` with hardcoded hex colors. Every other component uses Tailwind + shadcn/ui.

**Fix:** Rewrite both using Tailwind utility classes and shadcn/ui components (`Input`, `Button`, `Card`). Use CSS variables from `index.css` for theming consistency.

---

## Simplification (reduce code)

### 11. ~300 lines of duplicated API route boilerplate

All 6 entity route files repeat identical 5-endpoint structures with the same imports, signatures, and `PaginatedResponse` construction.

**Fix:** Add a `PaginatedResponse.from_result(items, total, pagination)` class method to eliminate the 4-line construction repeated in every list endpoint. Consider a `create_crud_router()` factory for entities with no custom logic (Accounts, Contacts, Leads). Keep manual routes for entities with special behavior (Opportunities, Cases). This alone removes ~150 lines.

### 12. Module-level service aliases are noise

Every service file exposes aliases like `get_account_by_id = account_service.get_by_id`. The routes import the module and call these aliases.

**Fix:** Import the service instance directly in routes: `from app.services.account import account_service`, then call `account_service.get_by_id(...)`. Remove all aliases.

### 13. ~1200 lines of duplicated frontend page logic

All 5 list pages and 5 detail pages follow an identical pattern with 10+ `useState` hooks, identical `load`/`handleCreate`/`handleDelete` functions.

**Fix:** Extract a `useEntityCRUD(api, defaultSort)` hook that encapsulates: items, total, loading, pagination, filters, load, create, update, delete. Each list page becomes ~50 lines of column/filter config instead of ~150. Similarly, extract a `useEntityDetail(api, id)` hook for detail pages.

### 14. Dead delete infrastructure on every list page

Every list page declares `deleteId` state and renders `DeleteConfirmDialog`, but nothing ever sets `deleteId` — no delete buttons exist on list rows.

**Fix:** Remove `deleteId` state and `DeleteConfirmDialog` from all list pages. Re-add when delete buttons are actually implemented.

### 15. Remove `type: ignore[return-value]` from all route handlers

Every route handler has `# type: ignore[return-value]`. This is a smell.

**Fix:** Return `EntityRead.model_validate(record)` explicitly instead of returning the ORM model raw. This also makes the type checker happy and ensures the response matches the declared schema.

### 16. Role hierarchy fake pagination hack

`RoleService.get_hierarchy` creates `type("P", (), {"offset": 0, "limit": 1000})()` — a dynamically typed class to fake pagination.

**Fix:** Add a `list_all(db, **filters)` method to `CRUDService` that doesn't require pagination, or just query directly in `get_hierarchy` without going through `self.list`.

---

## Small improvements (low-effort, high-value)

### 17. Escape `%` and `_` in `ilike` filters

All services pass user input directly into `ilike(f"%{value}%")`. While SQLAlchemy parameterizes the value, `%` and `_` in user input act as wildcards.

**Fix:** Add a `escape_like(value: str) -> str` utility that escapes `%`, `_`, and `\`, then use `ilike(f"%{escaped}%", escape="\\")` in all services.

### 18. Add `owner_id` filter to list endpoints

No entity list endpoint allows filtering by `owner_id`. "Show my records" is the most basic CRM filter.

**Fix:** Add `owner_id: int | None = Query(None)` to all entity list endpoints and pass it to the service.

### 19. Add lead status validation

`LeadCreate` accepts any string for `status`. All other entities with status/stage fields validate against an enum.

**Fix:** Add a `field_validator("status")` to `LeadCreate` and `LeadUpdate`, matching the pattern used in `OpportunityCreate` and `CaseCreate`.

### 20. Remove redundant `onupdate=func.now()` on `updated_at`

The column has `onupdate=func.now()` (ORM-level) AND there's a PostgreSQL trigger doing the same. Dual mechanisms are confusing.

**Fix:** Remove `onupdate=func.now()` from the SQLAlchemy model. The DB trigger is the authoritative source and works for non-ORM updates too.

### 21. Unused frontend dependencies

`@radix-ui/react-toast` is installed but never used. `separator.tsx` is installed but never imported.

**Fix:** Remove `@radix-ui/react-toast` from `package.json`. Delete `separator.tsx` from `components/ui/`. (Toast can be re-added properly when notifications are implemented.)

### 22. API client uses hard navigation on 401

The axios interceptor does `window.location.href = '/login'` instead of using React Router, causing a full app reset.

**Fix:** Use the auth store's `logout()` action and `window.location.replace('/login')` or, better, have the interceptor set an `isAuthenticated = false` flag that the router reacts to.

---

## Verification

After implementing the above:

1. `make ci` — full pipeline must pass (lint + test + build)
2. Run existing test suite — all current tests should still pass (bugs 1-4 may need new test assertions)
3. Manual check: create/update an opportunity with custom fields → should now validate
4. Manual check: create two cases concurrently → no 500 error
5. Manual check: login page and layout render correctly with Tailwind (no visual regression)
6. `grep -r "type: ignore\[return-value\]" backend/app/api/` — should return 0 results after item 15
7. Frontend: verify Contact create/update sends `mobile_phone` (not `mobile`)

---

## What NOT to do

- Don't build a generic CRUD router factory that handles all edge cases — the 3 simple entities (Accounts, Contacts, Leads) benefit from a helper, but Opportunities and Cases have enough custom logic to stay manual.
- Don't abstract `RecordForm` into a schema-driven form engine — just fix the type mismatches and add basic validation for now.
- Don't add refresh tokens, rate limiting, or Redis caching yet — those are P1 features, not MVP fixes.
- Don't write service-level tests right now — the API integration tests already cover the service layer indirectly. Service tests are a P1 item.

---

## Priority order

| Order | Items | Effort | Impact |
|-------|-------|--------|--------|
| 1 | Bugs #1-5 | Small | Prevents data corruption and 500 errors |
| 2 | Inconsistencies #6-7, #9 | Medium | Standardizes user entity, removes confusion |
| 3 | Frontend fixes #10, #14, #21-22 | Medium | Fixes broken theming, removes dead code |
| 4 | Simplification #11-12, #15 | Medium | Removes ~400 lines of boilerplate |
| 5 | Small improvements #17-20 | Small | Hardens input handling |
| 6 | Simplification #13, #16 | Medium | Reduces frontend duplication |
| 7 | Cleanup #8 | Small | Minor schema tidying |
# ─────────────────────────────────────────────────────────────────────────────
# OpenSalesClaw — Local CI Runner
#
# Mirrors the GitHub Actions pipeline (.github/workflows/ci.yml) so you can
# validate every step before pushing.
#
# Quick start:
#   make ci             # run the full pipeline (lint + test + build)
#   make lint           # backend (ruff + mypy) and frontend (eslint + tsc)
#   make test           # backend (pytest) and frontend (tsc)
#   make test-backend   # pytest with coverage only
#
# Prerequisites:
#   - uv          (https://docs.astral.sh/uv/)
#   - Node.js 20+ with npm
#   - Docker with the Compose plugin
# ─────────────────────────────────────────────────────────────────────────────

# ── Configuration ────────────────────────────────────────────────────────────

BACKEND_DIR  := backend
FRONTEND_DIR := frontend

# Must match the GitHub Actions service container values so test results
# are comparable. conftest.py reads DATABASE_URL (override=False), so these
# exported vars win over any local .env file.
# DATABASE_URL is intentionally NOT set here — it is derived at runtime from
# the running db container so it works regardless of local .env credentials.
export SECRET_KEY                := local-ci-test-secret-key-not-for-production
export ACCESS_TOKEN_EXPIRE_MINUTES := 30
export CORS_ORIGINS              := ["http://localhost:3000"]

DB_TEST     := opensalesclaw_test

# ── Default target ───────────────────────────────────────────────────────────

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo ""
	@echo "  OpenSalesClaw — local CI targets"
	@echo ""
	@echo "  make ci                Run the full pipeline (lint + test + build)"
	@echo "  make lint              Backend lint/type-check + frontend lint/tsc"
	@echo "  make lint-backend      ruff check, ruff format --check, mypy"
	@echo "  make lint-frontend     eslint, tsc --noEmit"
	@echo "  make test              Backend pytest + frontend tsc"
	@echo "  make test-backend      pytest with coverage (requires DB)"
	@echo "  make test-frontend     tsc --noEmit"
	@echo "  make db-test-ready     Start dev DB and create test database"
	@echo "  make build             docker compose build --no-cache"
	@echo ""

# ── Full pipeline ─────────────────────────────────────────────────────────────

.PHONY: ci
ci: lint test build
	@echo ""
	@echo "  ✓ All CI checks passed locally."
	@echo ""

# ── Lint ─────────────────────────────────────────────────────────────────────

.PHONY: lint
lint: lint-backend lint-frontend

.PHONY: lint-backend
lint-backend:
	@echo "── Backend: ruff lint ──────────────────────────────────────────────"
	cd $(BACKEND_DIR) && uv run ruff check .
	@echo "── Backend: ruff format check ──────────────────────────────────────"
	cd $(BACKEND_DIR) && uv run ruff format --check .
	@echo "── Backend: mypy ───────────────────────────────────────────────────"
	cd $(BACKEND_DIR) && uv run mypy app

.PHONY: lint-frontend
lint-frontend:
	@echo "── Frontend: install deps ──────────────────────────────────────────"
	cd $(FRONTEND_DIR) && npm ci --prefer-offline
	@echo "── Frontend: eslint ────────────────────────────────────────────────"
	cd $(FRONTEND_DIR) && npm run lint
	@echo "── Frontend: tsc --noEmit ──────────────────────────────────────────"
	cd $(FRONTEND_DIR) && npx tsc --noEmit

# ── Test ──────────────────────────────────────────────────────────────────────

.PHONY: test
test: test-backend test-frontend

.PHONY: db-test-ready
db-test-ready:
	@echo "── DB: ensuring dev postgres is running ────────────────────────────"
	docker compose up -d db
	@echo "── DB: waiting for postgres to be healthy ──────────────────────────"
	@for i in $$(seq 1 30); do \
		docker compose exec -T db pg_isready -q && break; \
		echo "  waiting… ($$i/30)"; \
		sleep 2; \
	done
	docker compose exec -T db pg_isready || (echo "ERROR: postgres did not become ready" && exit 1)
	@echo "── DB: creating test database if not exists ────────────────────────"
	@PG_USER=$$(docker compose exec -T db printenv POSTGRES_USER); \
	PG_DB=$$(docker compose exec -T db printenv POSTGRES_DB); \
	docker compose exec -T db psql -U $$PG_USER -d $$PG_DB -tc \
		"SELECT 1 FROM pg_database WHERE datname = '$(DB_TEST)'" \
		| grep -q 1 \
		|| docker compose exec -T db psql -U $$PG_USER -d $$PG_DB -c "CREATE DATABASE $(DB_TEST)"
	@echo "── DB: ready ───────────────────────────────────────────────────────"

.PHONY: test-backend
test-backend: db-test-ready
	@echo "── Backend: run migrations ─────────────────────────────────────────"
	@PG_USER=$$(docker compose exec -T db printenv POSTGRES_USER); \
	PG_PASS=$$(docker compose exec -T db printenv POSTGRES_PASSWORD); \
	export DATABASE_URL="postgresql+asyncpg://$$PG_USER:$$PG_PASS@localhost:5432/$(DB_TEST)"; \
	echo "  DATABASE_URL=$$DATABASE_URL"; \
	cd $(BACKEND_DIR) && uv run alembic upgrade head
	@echo "── Backend: pytest + coverage ──────────────────────────────────────"
	@PG_USER=$$(docker compose exec -T db printenv POSTGRES_USER); \
	PG_PASS=$$(docker compose exec -T db printenv POSTGRES_PASSWORD); \
	export DATABASE_URL="postgresql+asyncpg://$$PG_USER:$$PG_PASS@localhost:5432/$(DB_TEST)"; \
	cd $(BACKEND_DIR) && uv run pytest --cov=app --cov-report=term-missing --cov-fail-under=80

.PHONY: test-frontend
test-frontend:
	@echo "── Frontend: install deps ──────────────────────────────────────────"
	cd $(FRONTEND_DIR) && npm ci --prefer-offline
	@echo "── Frontend: tsc --noEmit ──────────────────────────────────────────"
	cd $(FRONTEND_DIR) && npx tsc --noEmit

# ── Build ─────────────────────────────────────────────────────────────────────

.PHONY: build
build:
	@echo "── Build: writing temporary .env ───────────────────────────────────"
	@printf '%s\n' \
		'DATABASE_URL=postgresql+asyncpg://opensalesclaw:opensalesclaw@db:5432/opensalesclaw' \
		'SECRET_KEY=ci-build-secret-key-not-for-production' \
		'ACCESS_TOKEN_EXPIRE_MINUTES=30' \
		'CORS_ORIGINS=["http://localhost:3000"]' \
		'POSTGRES_USER=opensalesclaw' \
		'POSTGRES_PASSWORD=opensalesclaw' \
		'POSTGRES_DB=opensalesclaw' \
		> .env.ci-build
	@echo "── Build: docker compose build --no-cache ──────────────────────────"
	docker compose --env-file .env.ci-build build --no-cache
	@rm -f .env.ci-build

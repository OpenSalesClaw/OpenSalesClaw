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
| **Database** | PostgreSQL |
| **API** | FastAPI (Python) |
| **ORM & Migrations** | SQLAlchemy + Alembic |
| **Validation** | Pydantic |
| **API Docs** | OpenAPI (auto-generated) |
| **Auth** | OAuth 2.0 |
| **Frontend** | React + Vite |
| **Containerisation** | Docker & Docker Compose |
| **Reverse Proxy / SSL** | Traefik |
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

# Start the stack
docker compose up -d

# Apply the database schema
docker compose exec db psql -U opensalesclaw -d opensalesclaw -f /schema/schema.sql
```

The API will be available at `http://localhost:8000` and interactive docs at `http://localhost:8000/docs`.

> **Note:** Detailed setup instructions, environment variable reference, and production deployment guides are coming soon.

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

For a deep dive, see [design/custom-tables-fields-architecture.md](design/custom-tables-fields-architecture.md).

---

## Project Structure

```
├── design/               # Architecture decision records & design docs
├── salesforce/            # Salesforce object metadata (CSVs) used as reference
│   └── objects/core/      # Account, Contact, Lead, Opportunity, Case, User, RecordType
├── schema/
│   └── schema.sql         # Full PostgreSQL schema (tables, indexes, triggers, seeds)
└── README.md
```

---

## Roadmap

OpenSalesClaw is in **early development**. Here's what's planned:

- [x] Core database schema (Accounts, Contacts, Leads, Opportunities, Cases, Users, Roles, RecordTypes)
- [x] Custom objects & custom fields architecture (JSONB + metadata tables)
- [x] Picklist management
- [x] Multi-currency support
- [ ] FastAPI REST endpoints for all core objects
- [ ] OAuth 2.0 authentication & authorization
- [ ] Alembic migration setup
- [ ] React frontend (list views, record detail, dashboards)
- [ ] Sales objects (Products, Pricebooks, Quotes, Orders, Contracts)
- [ ] Marketing objects (Campaigns, Campaign Members, Email Templates)
- [ ] Activity objects (Tasks, Events, Notes, Attachments)
- [ ] Reports & Dashboards engine
- [ ] Docker Compose production setup with Traefik
- [ ] CI/CD pipeline (GitHub Actions)
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

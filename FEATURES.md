# OpenSalesClaw — Feature Catalogue

> Exhaustive list of functional and technical features for a world-class, self-hostable CRM platform.
>
> **Priority legend**
> | Tag | Meaning |
> |-----|---------|
> | **MVP** | Minimum Viable Product — required for first usable release |
> | **P1** | Must Have — essential for production readiness |
> | **P2** | Should Have — expected by most CRM users |
> | **P3** | Nice to Have — differentiator / power-user feature |
>
> **Status legend:** `Not Started` · `In Design` · `In Progress` · `Done` · `Deferred`

---

## Table of Contents

1. [Core CRM Objects](#1-core-crm-objects)
2. [Sales](#2-sales)
3. [Marketing](#3-marketing)
4. [Service & Support](#4-service--support)
5. [Activities & Collaboration](#5-activities--collaboration)
6. [Analytics & Reporting](#6-analytics--reporting)
7. [Automation & Workflow](#7-automation--workflow)
8. [Customization & Metadata](#8-customization--metadata)
9. [User Management & Security](#9-user-management--security)
10. [Data Management](#10-data-management)
11. [Communication](#11-communication)
12. [Documents & Content](#12-documents--content)
13. [Integration & API](#13-integration--api)
14. [Internationalization & Localization](#14-internationalization--localization)
15. [Frontend & UX](#15-frontend--ux)
16. [Architecture & Infrastructure](#16-architecture--infrastructure)
17. [Database & Storage](#17-database--storage)
18. [Security & Compliance](#18-security--compliance)
19. [DevOps & Deployment](#19-devops--deployment)
20. [Developer Experience](#20-developer-experience)
21. [Performance & Scalability](#21-performance--scalability)
22. [Observability](#22-observability)

---

## 1. Core CRM Objects

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| F-CORE-001 | Accounts CRUD | Create, read, update, soft-delete company/organization records | MVP | Done |
| F-CORE-002 | Contacts CRUD | Manage individual people linked to accounts | MVP | Done |
| F-CORE-003 | Leads CRUD | Track unqualified prospects before conversion | MVP | Done |
| F-CORE-004 | Opportunities CRUD | Manage potential deals/sales with stage tracking | MVP | Done |
| F-CORE-005 | Cases CRUD | Customer support tickets/issues | MVP | Done |
| F-CORE-006 | Users CRUD | System user management (name, email, role, profile) | MVP | Done |
| F-CORE-007 | Roles & Role Hierarchy | Define organizational roles with parent-child hierarchy | MVP | Done |
| F-CORE-008 | Record Types | Sub-classify records within an object (e.g., "Partner Account") | P1 | Not Started |
| F-CORE-009 | Account Hierarchy | Parent-child relationships between accounts | P1 | Not Started |
| F-CORE-010 | Account-Contact Relationships | Many-to-many relationships between accounts and contacts | P1 | Not Started |
| F-CORE-011 | Person Accounts | Unified account + contact for B2C scenarios | P2 | Not Started |
| F-CORE-012 | Account Teams | Assign multiple users to an account with different roles | P2 | Not Started |
| F-CORE-013 | Contact Roles on Opportunities | Track contact involvement and influence on deals | P2 | Not Started |
| F-CORE-014 | Opportunity Teams | Collaborative selling — multiple users on a deal | P2 | Not Started |
| F-CORE-015 | Opportunity Splits | Revenue and credit splitting across team members | P3 | Not Started |
| F-CORE-016 | Partners | Track partner organizations and referral relationships | P3 | Not Started |
| F-CORE-017 | Competitors | Track competitive information on opportunities | P3 | Not Started |

---

## 2. Sales

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| F-SALES-001 | Opportunity Stages & Pipeline | Configurable sales stages with probability % | MVP | Done |
| F-SALES-002 | Lead Conversion | Convert a lead into account + contact + opportunity | P1 | Not Started |
| F-SALES-003 | Products | Product catalogue with descriptions, codes, and families | P1 | Not Started |
| F-SALES-004 | Price Books | Multiple price books (standard + custom) per currency/segment | P1 | Not Started |
| F-SALES-005 | Opportunity Line Items | Link products to opportunities with quantity, price, discount | P1 | Not Started |
| F-SALES-006 | Quotes | Generate quotes from opportunities with line items | P2 | Not Started |
| F-SALES-007 | Quote PDF Generation | Render quotes as downloadable/emailable PDFs | P2 | Not Started |
| F-SALES-008 | Orders | Convert quotes/opportunities into orders | P2 | Not Started |
| F-SALES-009 | Contracts | Manage customer contracts with terms and renewal dates | P2 | Not Started |
| F-SALES-010 | Lead Scoring | Rule-based or ML-based scoring to prioritize leads | P2 | Not Started |
| F-SALES-011 | Lead Assignment Rules | Auto-assign leads based on criteria (round-robin, territory, etc.) | P2 | Not Started |
| F-SALES-012 | Sales Forecasting | Roll-up pipeline by stage, owner, period; commit forecasts | P2 | Not Started |
| F-SALES-013 | Territory Management | Define sales territories and assign accounts/users | P3 | Not Started |
| F-SALES-014 | Revenue Schedules | Schedule recognized revenue over time for an opportunity | P3 | Not Started |
| F-SALES-015 | Sales Path / Guided Selling | Step-by-step guidance through sales stages with key fields | P3 | Not Started |
| F-SALES-016 | CPQ (Configure, Price, Quote) | Advanced product configuration with bundles, options, rules | P3 | Not Started |
| F-SALES-017 | Discount Approval Workflows | Approval chains for discounts exceeding thresholds | P3 | Not Started |
| F-SALES-018 | Win/Loss Analysis | Track and report on closed-won vs. closed-lost reasons | P2 | Not Started |
| F-SALES-019 | Duplicate Lead Detection | Detect and merge duplicate leads on creation or import | P2 | Not Started |

---

## 3. Marketing

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| F-MKT-001 | Campaigns | Create and manage marketing campaigns with budgets and status | P1 | Not Started |
| F-MKT-002 | Campaign Members | Add leads/contacts to campaigns with response status | P1 | Not Started |
| F-MKT-003 | Campaign Hierarchy | Parent-child campaign relationships for roll-up reporting | P2 | Not Started |
| F-MKT-004 | Campaign ROI Tracking | Track cost, revenue, and ROI per campaign | P2 | Not Started |
| F-MKT-005 | Email Templates | Reusable HTML/text templates with merge fields | P1 | Not Started |
| F-MKT-006 | Mass Email | Send bulk emails to leads/contacts with template support | P2 | Not Started |
| F-MKT-007 | Email Tracking | Track opens, clicks, bounces, and unsubscribes | P2 | Not Started |
| F-MKT-008 | Web-to-Lead Forms | Generate forms that create leads from website visitors | P2 | Not Started |
| F-MKT-009 | Web-to-Case Forms | Generate forms that create cases from website visitors | P2 | Not Started |
| F-MKT-010 | Landing Pages | Build simple landing pages for campaigns | P3 | Not Started |
| F-MKT-011 | Marketing Automation | Drip campaigns, nurture sequences, trigger-based emails | P3 | Not Started |
| F-MKT-012 | A/B Testing | Test email subject lines, content, send times | P3 | Not Started |
| F-MKT-013 | Lead Source Tracking | Track and report on lead sources and attribution | P1 | Not Started |
| F-MKT-014 | UTM Parameter Capture | Capture UTM tags from inbound web forms | P3 | Not Started |
| F-MKT-015 | Subscription / Consent Management | Manage opt-in/out preferences per communication channel | P2 | Not Started |
| F-MKT-016 | List Management | Create static and dynamic lists of leads/contacts | P2 | Not Started |

---

## 4. Service & Support

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| F-SVC-001 | Case Management | Full case lifecycle: new → working → escalated → closed | MVP | Done |
| F-SVC-002 | Case Assignment Rules | Auto-assign cases by criteria (product, region, priority) | P1 | Not Started |
| F-SVC-003 | Case Escalation Rules | Time-based escalation when cases aren't resolved | P2 | Not Started |
| F-SVC-004 | Case Queues | Shared queues for team-based case ownership | P2 | Not Started |
| F-SVC-005 | Case Comments | Internal and public comments on cases | P1 | Not Started |
| F-SVC-006 | Case Email-to-Case | Create cases from inbound emails | P2 | Not Started |
| F-SVC-007 | Knowledge Base | Searchable article library for support agents and customers | P2 | Not Started |
| F-SVC-008 | Knowledge Article Versioning | Draft, publish, archive lifecycle for articles | P3 | Not Started |
| F-SVC-009 | SLA Management | Define service level agreements with milestones and timers | P3 | Not Started |
| F-SVC-010 | Entitlements | Track customer support entitlements (e.g., hours, incidents) | P3 | Not Started |
| F-SVC-011 | Customer Portal | Self-service portal for customers to view/create cases | P3 | Not Started |
| F-SVC-012 | Case Satisfaction Surveys | Send CSAT surveys after case closure | P3 | Not Started |
| F-SVC-013 | Case Merge | Merge duplicate cases into a single record | P3 | Not Started |
| F-SVC-014 | Omni-Channel Routing | Route cases to agents across channels based on availability | P3 | Not Started |
| F-SVC-015 | Macros | One-click actions to perform repetitive case operations | P3 | Not Started |

---

## 5. Activities & Collaboration

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| F-ACT-001 | Tasks | Create, assign, and track tasks linked to any record | P1 | Not Started |
| F-ACT-002 | Events / Calendar | Schedule events with date, time, duration, and attendees | P1 | Not Started |
| F-ACT-003 | Activity Timeline | Chronological view of all activities on a record | P1 | Not Started |
| F-ACT-004 | Notes | Rich-text notes attached to any record | P1 | Not Started |
| F-ACT-005 | Call Logging | Log phone calls with outcome, duration, and notes | P2 | Not Started |
| F-ACT-006 | Email Logging | Associate sent/received emails with CRM records | P2 | Not Started |
| F-ACT-007 | Activity Feed / Chatter | Social feed for collaboration on records | P2 | Not Started |
| F-ACT-008 | @Mentions | Mention users in feed posts and comments | P2 | Not Started |
| F-ACT-009 | Follow Records | Subscribe to record updates and receive notifications | P2 | Not Started |
| F-ACT-010 | Shared Calendar | Team-wide calendar view for scheduling | P3 | Not Started |
| F-ACT-011 | Recurring Tasks & Events | Create repeating activities with configurable recurrence | P3 | Not Started |
| F-ACT-012 | Meeting Scheduler | Shareable availability links for external scheduling | P3 | Not Started |
| F-ACT-013 | Reminders & Notifications | In-app and email reminders for upcoming tasks and events | P2 | Not Started |

---

## 6. Analytics & Reporting

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| F-RPT-001 | Tabular Reports | List-style reports with filtering, sorting, and column selection | P1 | Not Started |
| F-RPT-002 | Summary Reports | Grouped/aggregated reports with subtotals | P1 | Not Started |
| F-RPT-003 | Matrix Reports | Cross-tab / pivot-table reports (rows × columns) | P2 | Not Started |
| F-RPT-004 | Report Filters | Standard, cross-object, and custom filter logic | P1 | Not Started |
| F-RPT-005 | Dashboards | Visual dashboards composed of report-backed components | P1 | Not Started |
| F-RPT-006 | Charts & Visualizations | Bar, line, pie, funnel, gauge, scatter charts | P1 | Not Started |
| F-RPT-007 | Dashboard Filters | Dynamic filters that apply across all dashboard components | P2 | Not Started |
| F-RPT-008 | Scheduled Reports | Email reports on a recurring schedule | P2 | Not Started |
| F-RPT-009 | Report Export | Export reports as CSV, Excel, PDF | P1 | Not Started |
| F-RPT-010 | Custom Report Types | Define report types spanning multiple related objects | P2 | Not Started |
| F-RPT-011 | Report Folders & Sharing | Organize reports in folders with role-based access | P2 | Not Started |
| F-RPT-012 | Real-Time Dashboards | Live-updating dashboard components | P3 | Not Started |
| F-RPT-013 | Embedded Analytics | Inline charts on record detail pages | P3 | Not Started |
| F-RPT-014 | Report Formulas | Custom calculated columns in reports | P3 | Not Started |
| F-RPT-015 | Pipeline Analytics | Visual pipeline funnel with stage-by-stage conversion rates | P2 | Not Started |
| F-RPT-016 | Sales Leaderboard | Gamified rep performance dashboards | P3 | Not Started |
| F-RPT-017 | Historical Trend Reporting | Track field changes over time for trending analysis | P3 | Not Started |

---

## 7. Automation & Workflow

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| F-AUTO-001 | Workflow Rules | IF-THEN rules triggered on record create/update | P1 | Not Started |
| F-AUTO-002 | Field Updates (Auto) | Automatically set field values based on conditions | P1 | Not Started |
| F-AUTO-003 | Email Alerts | Send templated emails when workflow conditions are met | P1 | Not Started |
| F-AUTO-004 | Approval Processes | Multi-step approval chains with approve/reject actions | P2 | Not Started |
| F-AUTO-005 | Assignment Rules | Auto-assign record ownership based on criteria | P1 | Not Started |
| F-AUTO-006 | Escalation Rules | Time-based escalation for unresolved records | P2 | Not Started |
| F-AUTO-007 | Scheduled Actions | Deferred actions triggered after a time delay | P2 | Not Started |
| F-AUTO-008 | Flow Builder (Visual) | Drag-and-drop visual automation builder | P3 | Not Started |
| F-AUTO-009 | Record-Triggered Flows | Complex multi-step logic on record events | P3 | Not Started |
| F-AUTO-010 | Outbound Messages | Send SOAP/HTTP messages to external systems on record events | P2 | Not Started |
| F-AUTO-011 | Validation Rules | Prevent saves when data doesn't meet criteria | P1 | Not Started |
| F-AUTO-012 | Formula Fields | Read-only calculated fields using expressions | P2 | Not Started |
| F-AUTO-013 | Roll-Up Summary Fields | Aggregate child record values on parent records | P2 | Not Started |
| F-AUTO-014 | Process Scheduling (Cron) | Schedule batch processes (cleanup, sync, reports) | P2 | Not Started |
| F-AUTO-015 | Auto-Response Rules | Auto-reply to web-to-lead/case submissions | P3 | Not Started |

---

## 8. Customization & Metadata

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| F-CUST-001 | Custom Fields | Add user-defined fields to any standard or custom object (JSONB) | MVP | Done |
| F-CUST-002 | Custom Field Types | Support text, number, date, datetime, boolean, picklist, lookup, email, URL, phone, currency, percent, textarea, rich text, formula, auto-number | MVP | In Progress |
| F-CUST-003 | Custom Objects | Create entirely new objects at runtime with full CRUD | P1 | Not Started |
| F-CUST-004 | Custom Field Definitions Table | Metadata-driven registry of all custom fields | MVP | Done |
| F-CUST-005 | Picklist Management | Create, edit, and reorder picklist values per field | MVP | Done |
| F-CUST-006 | Dependent Picklists | Cascade picklist values based on a controlling field | P2 | Not Started |
| F-CUST-007 | Multi-Select Picklists | Allow multiple picklist value selections | P2 | Not Started |
| F-CUST-008 | Global Picklist Value Sets | Shared picklist definitions reusable across fields | P3 | Not Started |
| F-CUST-009 | Page Layouts | Configure field arrangement and sections per object per record type | P2 | Not Started |
| F-CUST-010 | Compact Layouts | Define which fields appear in card/hover views | P3 | Not Started |
| F-CUST-011 | Related Lists Configuration | Choose and order related lists on record detail pages | P2 | Not Started |
| F-CUST-012 | Custom Tabs | Surface custom objects and pages in the navigation | P2 | Not Started |
| F-CUST-013 | Custom Applications | Group tabs and objects into logical apps (Sales, Service, etc.) | P3 | Not Started |
| F-CUST-014 | Lookup Filters | Restrict lookup field results based on criteria | P3 | Not Started |
| F-CUST-015 | Record Type-Specific Layouts | Different page layouts per record type | P2 | Not Started |
| F-CUST-016 | Custom Labels | Admin-managed translatable label strings | P3 | Not Started |
| F-CUST-017 | Metadata API | Programmatic access to object/field/layout definitions | P2 | Not Started |
| F-CUST-018 | Schema Builder (Visual) | Visual tool to view/edit object relationships | P3 | Not Started |

---

## 9. User Management & Security

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| F-SEC-001 | User Authentication (OAuth 2.0) | Login via OAuth 2.0 / OpenID Connect | MVP | In Progress |
| F-SEC-002 | Username/Password Login | Local credential authentication with bcrypt hashing | MVP | Done |
| F-SEC-003 | Multi-Factor Authentication (MFA) | TOTP-based second factor | P1 | Not Started |
| F-SEC-004 | SSO (SAML / OIDC) | Single sign-on with external IdPs (Okta, Azure AD, Google) | P2 | Not Started |
| F-SEC-005 | Profiles | Define base-level object & field permissions per profile | P1 | Not Started |
| F-SEC-006 | Permission Sets | Additive permissions layered on top of profiles | P2 | Not Started |
| F-SEC-007 | Permission Set Groups | Group multiple permission sets for assignment | P3 | Not Started |
| F-SEC-008 | Role Hierarchy | Control record visibility through organizational hierarchy | P1 | Done |
| F-SEC-009 | Organization-Wide Defaults (OWD) | Default sharing level per object (Private, Public Read, Public R/W) | P1 | Not Started |
| F-SEC-010 | Sharing Rules | Criteria-based and owner-based sharing rules | P2 | Not Started |
| F-SEC-011 | Manual Record Sharing | Users can share individual records with other users/groups | P2 | Not Started |
| F-SEC-012 | Field-Level Security | Control field visibility and editability per profile | P1 | Not Started |
| F-SEC-013 | Login History & Tracking | Log all login attempts with IP, device, and result | P1 | Not Started |
| F-SEC-014 | Session Management | Active session list, forced logout, session timeout config | P1 | Not Started |
| F-SEC-015 | IP Allow-listing | Restrict login to trusted IP ranges | P2 | Not Started |
| F-SEC-016 | Password Policies | Configurable complexity, expiration, and history rules | P1 | Not Started |
| F-SEC-017 | Public Groups | Organize users and roles into groups for sharing | P2 | Not Started |
| F-SEC-018 | Delegated Administration | Allow non-admins to manage users in their branch | P3 | Not Started |
| F-SEC-019 | API Token Management | Issue and revoke scoped API tokens per user | P1 | Not Started |
| F-SEC-020 | CORS Configuration | Configurable allowed origins for API requests | P1 | Not Started |
| F-SEC-021 | CSRF Protection | Token-based CSRF protection for state-changing requests | P1 | Not Started |
| F-SEC-022 | Data Encryption at Rest | Encrypt sensitive columns (PII) in the database | P2 | Not Started |
| F-SEC-023 | TLS / HTTPS Enforcement | Require encrypted connections for all traffic | P1 | Not Started |
| F-SEC-024 | Rate Limiting | Per-user and per-IP request rate limits | P1 | Not Started |
| F-SEC-025 | Admin User Management UI | Superuser-only admin panel: paginated user list with email/status filters, create user (email, password, role, is_active, is_superuser), edit, admin-initiated password reset, soft-delete; self-protection guards block deactivating or deleting one's own account | P1 | Done |
| F-SEC-026 | Admin Role Management UI | Superuser-only admin panel: role hierarchy tree view with expand/collapse nodes, create/edit/delete roles, child roles list, assigned users list | P1 | Done |
| F-SEC-027 | Public Registration Control | `ALLOW_PUBLIC_REGISTRATION` config flag; when `false`, `POST /api/auth/register` returns 403 and new users must be created by a superuser via `POST /api/users` | P1 | Done |

---

## 10. Data Management

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| F-DATA-001 | CSV Import | Bulk import records from CSV files with field mapping | P1 | Not Started |
| F-DATA-002 | CSV Export | Export list views and report results to CSV | P1 | Not Started |
| F-DATA-003 | Data Loader (Bulk API) | High-volume insert, update, upsert, delete via API | P2 | Not Started |
| F-DATA-004 | Duplicate Detection Rules | Define match rules to flag potential duplicates | P2 | Not Started |
| F-DATA-005 | Record Merge | Merge duplicate records preserving related data | P2 | Not Started |
| F-DATA-006 | Mass Update | Bulk-edit field values across multiple records | P2 | Not Started |
| F-DATA-007 | Mass Transfer | Reassign record ownership in bulk | P2 | Not Started |
| F-DATA-008 | Recycle Bin | View and restore soft-deleted records | P1 | Not Started |
| F-DATA-009 | Hard Delete (Admin) | Permanently remove records from the recycle bin | P2 | Not Started |
| F-DATA-010 | Data Validation on Import | Validate imported data against field types and rules | P1 | Not Started |
| F-DATA-011 | Salesforce Data Import | Import from Salesforce exports (with sfid mapping) | P2 | Not Started |
| F-DATA-012 | Sandbox / Seed Data | Generate realistic sample data for dev/test environments | P2 | Not Started |
| F-DATA-013 | Field History Tracking | Track changes to selected fields with old/new values and timestamps | P2 | Not Started |
| F-DATA-014 | Audit Trail | Full audit log of admin/config changes | P1 | Not Started |
| F-DATA-015 | Data Archival Policies | Archive old records to reduce active dataset size | P3 | Not Started |
| F-DATA-016 | External Data Sources | Virtual objects backed by external APIs | P3 | Not Started |
| F-DATA-017 | Data Dictionary / Catalog | Auto-generated documentation of all objects and fields | P3 | Not Started |

---

## 11. Communication

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| F-COMM-001 | Outbound Email (SMTP) | Send emails from the CRM via configurable SMTP | P1 | Not Started |
| F-COMM-002 | Email Templates with Merge Fields | Dynamic template rendering with record data | P1 | Not Started |
| F-COMM-003 | Email-to-Case | Parse inbound emails into case records | P2 | Not Started |
| F-COMM-004 | Email Tracking (Opens/Clicks) | Pixel and link tracking for sent emails | P2 | Not Started |
| F-COMM-005 | Inbound Email Parsing | Match inbound emails to existing records | P3 | Not Started |
| F-COMM-006 | SMS Sending | Send SMS messages (via Twilio/provider integration) | P3 | Not Started |
| F-COMM-007 | In-App Notifications | Real-time notifications for assignments, mentions, approvals | P1 | Not Started |
| F-COMM-008 | Push Notifications | Browser push notifications for important events | P3 | Not Started |
| F-COMM-009 | Notification Preferences | Per-user channel preferences (email, in-app, push) | P2 | Not Started |
| F-COMM-010 | Unified Inbox | Aggregated view of all communication per record | P3 | Not Started |

---

## 12. Documents & Content

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| F-DOC-001 | File Attachments | Upload files to any record (local or S3-compatible storage) | P1 | Not Started |
| F-DOC-002 | File Preview | In-app preview for images and PDFs | P2 | Not Started |
| F-DOC-003 | File Size & Type Limits | Admin-configurable upload constraints | P1 | Not Started |
| F-DOC-004 | Storage Backend Abstraction | Pluggable storage (local filesystem, S3, MinIO, GCS) | P1 | Not Started |
| F-DOC-005 | Document Versioning | Track file revisions with version history | P3 | Not Started |
| F-DOC-006 | Content Library | Shared folder of assets (logos, brochures, templates) | P3 | Not Started |
| F-DOC-007 | Document Generation | Generate documents from templates and record data | P3 | Not Started |

---

## 13. Integration & API

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| F-INT-001 | RESTful CRUD API | Full CRUD endpoints for every object with filtering, sorting, pagination | MVP | Done |
| F-INT-002 | OpenAPI / Swagger Docs | Auto-generated interactive API documentation | MVP | Done |
| F-INT-003 | API Versioning | Version the API (URL or header-based) for backward compatibility | P1 | Not Started |
| F-INT-004 | Webhooks (Outbound) | Configurable HTTP callbacks on record events (create, update, delete) | P1 | Not Started |
| F-INT-005 | Webhook Management UI | Admin interface to create, test, and monitor webhooks | P2 | Not Started |
| F-INT-006 | Webhook Retry & Dead-Letter | Retry failed webhook deliveries; dead-letter queue for inspection | P2 | Not Started |
| F-INT-007 | Inbound Webhooks | Accept events from external systems via signed webhook endpoints | P2 | Not Started |
| F-INT-008 | Bulk API | High-throughput batch endpoints for import/export | P2 | Not Started |
| F-INT-009 | GraphQL API | GraphQL endpoint for flexible querying | P3 | Not Started |
| F-INT-010 | Event Bus / Streaming | Real-time event stream (SSE or WebSocket) for record changes | P3 | Not Started |
| F-INT-011 | Zapier / n8n Integration | Pre-built connectors for popular automation platforms | P3 | Not Started |
| F-INT-012 | Google Workspace Integration | Sync contacts, calendar events, and emails with Google | P3 | Not Started |
| F-INT-013 | Microsoft 365 Integration | Sync contacts, calendar events, and emails with Outlook | P3 | Not Started |
| F-INT-014 | Slack Integration | Notifications, record lookup, and actions from Slack | P3 | Not Started |
| F-INT-015 | Plugin / Extension System | Allow third-party extensions via a defined plugin API | P3 | Not Started |
| F-INT-016 | Connected Apps | Register external apps with OAuth client credentials | P2 | Not Started |
| F-INT-017 | SOQL-like Query Language | Provide a structured query language for API consumers | P3 | Not Started |

---

## 14. Internationalization & Localization

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| F-I18N-001 | Multi-Currency Support | ISO 4217 currencies with conversion rates on records | P1 | Not Started |
| F-I18N-002 | Currency Conversion Rates | Admin-managed or API-fetched exchange rate tables | P2 | Not Started |
| F-I18N-003 | Dated Exchange Rates | Historical conversion rates for accurate reporting | P3 | Not Started |
| F-I18N-004 | Timezone Handling | Store UTC; display in user's configured timezone | MVP | Not Started |
| F-I18N-005 | Locale-Aware Formatting | Format dates, numbers, and currency per user locale | P1 | Not Started |
| F-I18N-006 | Multi-Language UI (i18n) | Translate UI strings; allow language packs | P2 | Not Started |
| F-I18N-007 | Translated Picklist Values | Localized labels for picklist options | P3 | Not Started |
| F-I18N-008 | RTL Layout Support | Support right-to-left languages (Arabic, Hebrew) | P3 | Not Started |

---

## 15. Frontend & UX

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| F-UI-001 | List Views | Filterable, sortable, paginated record lists per object | MVP | Not Started |
| F-UI-002 | Record Detail Pages | View and edit all fields on a single record | MVP | Not Started |
| F-UI-003 | Record Create / Edit Forms | Dynamic forms driven by field metadata and layouts | MVP | Not Started |
| F-UI-004 | Global Search | Search across all objects by keyword | P1 | Not Started |
| F-UI-005 | Inline Editing | Edit field values directly on list views and detail pages | P1 | Not Started |
| F-UI-006 | Navigation / App Bar | Configurable top navigation with object tabs | MVP | Not Started |
| F-UI-007 | Home Page | Personalized dashboard with tasks, recent records, metrics | P1 | Not Started |
| F-UI-008 | Related Lists | Display child/related records on parent detail pages | P1 | Not Started |
| F-UI-009 | Kanban Board View | Drag-and-drop board view for opportunities, cases, etc. | P2 | Not Started |
| F-UI-010 | Split View | Master-detail layout for record browsing | P2 | Not Started |
| F-UI-011 | Mobile-Responsive Design | Fully functional on tablet and mobile browsers | P1 | Not Started |
| F-UI-012 | Progressive Web App (PWA) | Installable, offline-capable mobile experience | P3 | Not Started |
| F-UI-013 | Dark Mode | System and manual dark-mode toggle | P3 | Not Started |
| F-UI-014 | Keyboard Shortcuts | Power-user shortcuts for navigation and actions | P3 | Not Started |
| F-UI-015 | Drag-and-Drop Stage Updates | Move opportunities/cases between stages via drag-and-drop | P2 | Not Started |
| F-UI-016 | Toast / Snackbar Notifications | Non-blocking success/error feedback messages | P1 | Not Started |
| F-UI-017 | Loading Skeletons | Skeleton screens during data loading | P2 | Not Started |
| F-UI-018 | Empty States | Helpful empty-state illustrations with CTAs | P2 | Not Started |
| F-UI-019 | Breadcrumbs | Contextual breadcrumb navigation | P1 | Not Started |
| F-UI-020 | Customizable Home Tabs | Users choose which objects/tabs to pin | P2 | Not Started |
| F-UI-021 | Theme Customization | Configurable brand colors and logo | P2 | Not Started |
| F-UI-022 | Accessibility (WCAG 2.1 AA) | Keyboard navigation, screen reader support, contrast ratios | P1 | Not Started |
| F-UI-023 | Onboarding / Setup Wizard | Guided first-run configuration for new instances | P2 | Not Started |

---

## 16. Architecture & Infrastructure

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| T-ARCH-001 | FastAPI Application Scaffold | Project structure with routers, models, schemas, services | MVP | Not Started |
| T-ARCH-002 | React + Vite Scaffold | Frontend project with TypeScript, routing, API client, and Tailwind CSS + shadcn/ui | MVP | Done |
| T-ARCH-002a | shadcn/ui Setup | Install Tailwind CSS, initialize shadcn/ui, configure CSS variables and theme in `index.css` | MVP | Done |
| T-ARCH-003 | Docker Compose (Dev) | One-command local dev environment (API + DB + frontend) | MVP | Done |
| T-ARCH-004 | Docker Compose (Production) | Production-ready compose with Traefik reverse proxy | P1 | Done |
| T-ARCH-005 | Environment Configuration | 12-factor config via environment variables with validation | MVP | Not Started |
| T-ARCH-006 | Background Job Queue | Async task processing (Celery, ARQ, or Dramatiq + Redis) | P1 | Not Started |
| T-ARCH-007 | Event System (Internal) | Pub/sub for decoupled domain events within the backend | P2 | Not Started |
| T-ARCH-008 | Caching Layer (Redis) | Cache frequently accessed data (config, picklists, metadata) | P1 | Not Started |
| T-ARCH-009 | WebSocket Support | Real-time push for notifications and live updates | P2 | Not Started |
| T-ARCH-010 | Multi-Tenant Architecture | Schema-based or row-based tenant isolation | P3 | Not Started |
| T-ARCH-011 | Horizontal Scaling | Stateless API servers behind a load balancer | P2 | Not Started |
| T-ARCH-012 | Service Health Checks | `/health` and `/ready` endpoints for orchestrators | MVP | Not Started |
| T-ARCH-013 | Graceful Shutdown | Handle SIGTERM cleanly; drain connections before exit | P1 | Not Started |
| T-ARCH-014 | Feature Flags | Toggle features on/off without redeployment | P3 | Not Started |
| T-ARCH-015 | Plugin Architecture | Extensible hook system for custom business logic | P3 | Not Started |
| T-ARCH-016 | Separate Admin Shell | Distinct `/admin` area with its own `AdminLayout` sidebar (Back-to-CRM link, extensible nav), `AdminRoute` superuser guard (redirects non-admins to `/`), and `AdminPageRoute` wrapper; fully isolated from main CRM routing | MVP | Done |

---

## 17. Database & Storage

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| T-DB-001 | PostgreSQL Schema Design | Full schema for all core objects with conventions from copilot-instructions | MVP | Done |
| T-DB-002 | Alembic Migration Setup | Migration framework with auto-generation and version tracking | MVP | Done |
| T-DB-003 | BaseModel Mixin | Shared SQLAlchemy mixin for id, sfid, audit cols, soft-delete, custom_fields | MVP | Done |
| T-DB-004 | JSONB Custom Fields with GIN Index | Custom field storage with performant querying | MVP | Done |
| T-DB-005 | Full-Text Search (tsvector) | PostgreSQL full-text search across key fields | P1 | Not Started |
| T-DB-006 | Database Connection Pooling | SQLAlchemy async pool + PgBouncer for production | P1 | Not Started |
| T-DB-007 | Read Replicas | Support routing read queries to replica databases | P3 | Not Started |
| T-DB-008 | Database Seeding Scripts | Populate reference data (picklists, record types, admin user) | P1 | Done |
| T-DB-009 | `updated_at` Trigger | PostgreSQL trigger to auto-set `updated_at` on every UPDATE | MVP | Not Started |
| T-DB-010 | Soft-Delete Query Filter | Default query filter excluding `is_deleted = TRUE` records | MVP | Done |
| T-DB-011 | Indexing Strategy | Indexes on foreign keys, frequently filtered/sorted columns | P1 | Not Started |
| T-DB-012 | Database Backup & Restore | Automated pg_dump backups with point-in-time restore | P1 | Not Started |
| T-DB-013 | Object-Level Storage (S3/MinIO) | Blob storage for file attachments | P1 | Not Started |
| T-DB-014 | Database Partitioning | Table partitioning for high-volume tables (e.g., activities, audit logs) | P3 | Not Started |

---

## 18. Security & Compliance

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| T-SEC-001 | Input Validation & Sanitization | Pydantic validation on all inputs; escape outputs | MVP | Not Started |
| T-SEC-002 | SQL Injection Prevention | Parameterized queries via SQLAlchemy (no raw SQL with user input) | MVP | Not Started |
| T-SEC-003 | XSS Prevention | Sanitize HTML in rich text fields; CSP headers | P1 | Not Started |
| T-SEC-004 | Secrets Management | No secrets in code; support `.env`, Docker secrets, Vault | MVP | Not Started |
| T-SEC-005 | Dependency Vulnerability Scanning | Automated CVE scanning (Dependabot, pip-audit, npm audit) | P1 | Not Started |
| T-SEC-006 | GDPR Compliance | Data export, right to erasure, consent tracking | P2 | Not Started |
| T-SEC-007 | Data Retention Policies | Configurable auto-purge rules for old/deleted data | P3 | Not Started |
| T-SEC-008 | Audit Log (Security Events) | Log auth events, permission changes, data exports | P1 | Not Started |
| T-SEC-009 | Penetration Testing Readiness | Hardened config, security headers, OWASP Top 10 coverage | P2 | Not Started |
| T-SEC-010 | Content Security Policy (CSP) | Strict CSP headers to prevent script injection | P1 | Not Started |
| T-SEC-011 | Cookie Security | HttpOnly, Secure, SameSite flags on all cookies | P1 | Not Started |
| T-SEC-012 | RBAC Enforcement Middleware | Centralized permission checks before every API operation | P1 | Not Started |

---

## 19. DevOps & Deployment

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| T-OPS-001 | Dockerfile (Backend) | Multi-stage Docker build for the FastAPI app | MVP | Done |
| T-OPS-002 | Dockerfile (Frontend) | Multi-stage build: Vite build → Nginx serving | MVP | Done |
| T-OPS-003 | CI Pipeline (GitHub Actions) | Lint, type-check, test, build on every PR | P1 | Not Started |
| T-OPS-004 | CD Pipeline (GitHub Actions) | Auto-deploy to staging on merge; manual promote to prod | P2 | Not Started |
| T-OPS-005 | Traefik Reverse Proxy | TLS termination, routing, automatic Let's Encrypt certs | P1 | Not Started |
| T-OPS-006 | Helm Chart / K8s Manifests | Kubernetes deployment option | P3 | Not Started |
| T-OPS-007 | Automated Database Migrations | Run Alembic migrations on deploy (init container or entrypoint) | P1 | Done |
| T-OPS-008 | Blue/Green or Rolling Deploys | Zero-downtime deployment strategy | P3 | Not Started |
| T-OPS-009 | Automatic TLS Certificates | Let's Encrypt integration via Traefik or Caddy | P1 | Not Started |
| T-OPS-010 | Docker Image Registry | Publish images to GHCR or Docker Hub | P2 | Not Started |
| T-OPS-011 | Infrastructure-as-Code Examples | Terraform / Pulumi examples for AWS, GCP, DigitalOcean | P3 | Not Started |
| T-OPS-012 | One-Click Install Script | Bash/shell script for quick self-hosted setup | P2 | Not Started |

---

## 20. Developer Experience

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| T-DX-001 | OpenAPI Auto-Generated Docs | Swagger UI and ReDoc served at `/docs` and `/redoc` | MVP | Done |
| T-DX-002 | Hot Reload (Backend) | Uvicorn `--reload` for fast dev iteration | MVP | Not Started |
| T-DX-003 | Hot Reload (Frontend) | Vite HMR for instant frontend updates | MVP | Not Started |
| T-DX-004 | Makefile / Task Runner | `make dev`, `make test`, `make migrate`, etc. | P1 | Not Started |
| T-DX-005 | Pre-Commit Hooks | ruff lint, black format, mypy type-check on commit | P1 | Not Started |
| T-DX-006 | Contributing Guide | `CONTRIBUTING.md` with setup, conventions, and PR process | P1 | Not Started |
| T-DX-007 | Architecture Decision Records | Document key design decisions in `design/` | P1 | Not Started |
| T-DX-008 | Postman / Bruno Collection | Pre-built API request collection for testing | P2 | Not Started |
| T-DX-009 | Type-Safe API Client (Frontend) | Auto-generate TypeScript types from OpenAPI schema | P1 | Not Started |
| T-DX-010 | Database ERD Generation | Auto-generate entity-relationship diagrams from schema | P2 | Not Started |
| T-DX-011 | Dev Container / Codespaces | VS Code dev container for consistent dev environments | P2 | Not Started |
| T-DX-012 | Storybook (Component Library) | Isolated UI component development and documentation | P3 | Not Started |

---

## 21. Performance & Scalability

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| T-PERF-001 | Async Database Sessions | Non-blocking DB access via SQLAlchemy async engine | MVP | Done |
| T-PERF-002 | Pagination (Offset/Limit) | All list endpoints paginated with configurable limits | MVP | Done |
| T-PERF-003 | Cursor-Based Pagination | Keyset pagination for large datasets and infinite scroll | P2 | Not Started |
| T-PERF-004 | Selective Field Retrieval | `?fields=id,name,email` parameter to reduce payload size | P2 | Not Started |
| T-PERF-005 | Response Compression (gzip/br) | Compress API responses for reduced bandwidth | P1 | Not Started |
| T-PERF-006 | Query Optimization & N+1 Prevention | Eager loading, joined loads, and query analysis | P1 | Not Started |
| T-PERF-007 | Redis Caching | Cache picklists, metadata, session data, and hot queries | P1 | Not Started |
| T-PERF-008 | HTTP Caching Headers | ETag and Cache-Control for static and semi-static resources | P2 | Not Started |
| T-PERF-009 | CDN for Static Assets | Serve frontend bundles and files from a CDN | P3 | Not Started |
| T-PERF-010 | Lazy Loading (Frontend) | Code-split routes and heavy components | P1 | Not Started |
| T-PERF-011 | Virtualized Lists | Virtual scroll for large record lists in the UI | P2 | Not Started |
| T-PERF-012 | Database Query Logging (Slow Queries) | Log and alert on queries exceeding a configurable threshold | P1 | Not Started |
| T-PERF-013 | Load Testing Suite | k6 or Locust scripts for performance benchmarking | P3 | Not Started |

---

## 22. Observability

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| T-OBS-001 | Structured Logging (JSON) | JSON-formatted logs with correlation IDs per request | P1 | Not Started |
| T-OBS-002 | Log Levels & Configuration | Runtime-configurable log levels (DEBUG → CRITICAL) | P1 | Not Started |
| T-OBS-003 | Request ID / Correlation ID | Unique ID propagated through all log entries for a request | P1 | Not Started |
| T-OBS-004 | Metrics Endpoint (Prometheus) | `/metrics` endpoint exposing request counts, latency, DB pool stats | P2 | Not Started |
| T-OBS-005 | Distributed Tracing (OpenTelemetry) | End-to-end tracing across API, DB, cache, and background jobs | P3 | Not Started |
| T-OBS-006 | Error Tracking (Sentry) | Automatic exception capture and grouping | P1 | Not Started |
| T-OBS-007 | Grafana Dashboards | Pre-built dashboards for API, database, and infrastructure metrics | P2 | Not Started |
| T-OBS-008 | Alerting Rules | Configurable alerts on error rate, latency, disk, and memory | P2 | Not Started |
| T-OBS-009 | Uptime Monitoring | External health checks with incident notifications | P2 | Not Started |

---

## 23. Testing

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| T-TEST-001 | Unit Tests (Backend) | pytest tests for services, models, and utility functions | MVP | Done |
| T-TEST-002 | API Integration Tests | Test all CRUD endpoints with real DB (test transactions) | MVP | Not Started |
| T-TEST-003 | Test Fixtures & Factories | factory_boy factories for all entities | P1 | Not Started |
| T-TEST-004 | Frontend Unit Tests | Vitest/Jest tests for components and hooks | P1 | Not Started |
| T-TEST-005 | E2E Tests | Playwright or Cypress browser tests for critical flows | P2 | Not Started |
| T-TEST-006 | Test Coverage Reporting | Coverage reports with minimum thresholds in CI | P1 | Not Started |
| T-TEST-007 | Contract Testing | API schema validation between frontend and backend | P3 | Not Started |
| T-TEST-008 | Mutation Testing | Validate test quality with mutation analysis | P3 | Not Started |
| T-TEST-009 | Visual Regression Testing | Screenshot-based UI comparison (e.g., Chromatic) | P3 | Not Started |
| T-TEST-010 | Security Testing (OWASP ZAP) | Automated DAST scanning in CI | P3 | Not Started |

---

## Summary

| Priority | Count |
|----------|-------|
| **MVP**  | 35    |
| **P1**   | 69    |
| **P2**   | 72    |
| **P3**   | 57    |
| **Total**| **233** |
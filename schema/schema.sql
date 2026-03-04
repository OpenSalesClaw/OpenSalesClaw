-- =============================================================================
-- OpenSalesClaw — PostgreSQL Schema
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Trigger function: auto-set updated_at on every UPDATE
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- =============================================================================
-- TABLE: users
-- =============================================================================
CREATE TABLE users (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sfid                VARCHAR(40),
    email               VARCHAR(255) NOT NULL,
    hashed_password     VARCHAR(255) NOT NULL,
    first_name          VARCHAR(100),
    last_name           VARCHAR(100),
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    is_superuser        BOOLEAN NOT NULL DEFAULT FALSE,
    custom_fields       JSONB NOT NULL DEFAULT '{}'::jsonb,
    owner_id            BIGINT,              -- self-referential; FK added below
    created_by_id       BIGINT,
    updated_by_id       BIGINT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_deleted          BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at          TIMESTAMPTZ,
    deleted_by_id       BIGINT,
    role_id             BIGINT,              -- FK to roles; added after roles table creation
    CONSTRAINT uq_users_email UNIQUE (email)
);

ALTER TABLE users
    ADD CONSTRAINT fk_users_owner_id      FOREIGN KEY (owner_id)      REFERENCES users(id),
    ADD CONSTRAINT fk_users_created_by_id FOREIGN KEY (created_by_id) REFERENCES users(id),
    ADD CONSTRAINT fk_users_updated_by_id FOREIGN KEY (updated_by_id) REFERENCES users(id),
    ADD CONSTRAINT fk_users_deleted_by_id FOREIGN KEY (deleted_by_id) REFERENCES users(id),
    ADD CONSTRAINT fk_users_role_id        FOREIGN KEY (role_id)        REFERENCES roles(id);

CREATE INDEX idx_users_email      ON users (email);
CREATE INDEX idx_users_owner_id   ON users (owner_id);
CREATE INDEX idx_users_custom_fields ON users USING GIN (custom_fields);

CREATE TRIGGER trg_users_set_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- =============================================================================
-- TABLE: roles
-- =============================================================================
CREATE TABLE roles (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sfid                VARCHAR(40),
    name                VARCHAR(255) NOT NULL,
    parent_role_id      BIGINT REFERENCES roles(id),
    description         TEXT,
    custom_fields       JSONB NOT NULL DEFAULT '{}'::jsonb,
    owner_id            BIGINT REFERENCES users(id),
    created_by_id       BIGINT REFERENCES users(id),
    updated_by_id       BIGINT REFERENCES users(id),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_deleted          BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at          TIMESTAMPTZ,
    deleted_by_id       BIGINT REFERENCES users(id),
    CONSTRAINT uq_roles_name UNIQUE (name)
);

CREATE INDEX idx_roles_parent_role_id   ON roles (parent_role_id);
CREATE INDEX idx_roles_owner_id         ON roles (owner_id);
CREATE INDEX idx_roles_custom_fields    ON roles USING GIN (custom_fields);

CREATE TRIGGER trg_roles_set_updated_at
    BEFORE UPDATE ON roles
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- =============================================================================
-- TABLE: accounts
-- =============================================================================
CREATE TABLE accounts (
    id                      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sfid                    VARCHAR(40),
    name                    VARCHAR(255) NOT NULL,
    type                    VARCHAR(50),       -- Customer, Partner, Prospect, Vendor, Other
    industry                VARCHAR(100),
    website                 VARCHAR(255),
    phone                   VARCHAR(40),
    billing_street          VARCHAR(255),
    billing_city            VARCHAR(100),
    billing_state           VARCHAR(100),
    billing_postal_code     VARCHAR(20),
    billing_country         VARCHAR(100),
    description             TEXT,
    annual_revenue          NUMERIC(18, 2),
    number_of_employees     INTEGER,
    custom_fields           JSONB NOT NULL DEFAULT '{}'::jsonb,
    owner_id                BIGINT REFERENCES users(id),
    created_by_id           BIGINT REFERENCES users(id),
    updated_by_id           BIGINT REFERENCES users(id),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_deleted              BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at              TIMESTAMPTZ,
    deleted_by_id           BIGINT REFERENCES users(id)
);

CREATE INDEX idx_accounts_name         ON accounts (name);
CREATE INDEX idx_accounts_owner_id     ON accounts (owner_id);
CREATE INDEX idx_accounts_custom_fields ON accounts USING GIN (custom_fields);

CREATE TRIGGER trg_accounts_set_updated_at
    BEFORE UPDATE ON accounts
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- =============================================================================
-- TABLE: contacts
-- =============================================================================
CREATE TABLE contacts (
    id                      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sfid                    VARCHAR(40),
    account_id              BIGINT REFERENCES accounts(id),
    first_name              VARCHAR(100),
    last_name               VARCHAR(100) NOT NULL,
    email                   VARCHAR(255),
    phone                   VARCHAR(40),
    mobile_phone            VARCHAR(40),
    title                   VARCHAR(128),
    department              VARCHAR(100),
    mailing_street          VARCHAR(255),
    mailing_city            VARCHAR(100),
    mailing_state           VARCHAR(100),
    mailing_postal_code     VARCHAR(20),
    mailing_country         VARCHAR(100),
    custom_fields           JSONB NOT NULL DEFAULT '{}'::jsonb,
    owner_id                BIGINT REFERENCES users(id),
    created_by_id           BIGINT REFERENCES users(id),
    updated_by_id           BIGINT REFERENCES users(id),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_deleted              BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at              TIMESTAMPTZ,
    deleted_by_id           BIGINT REFERENCES users(id)
);

CREATE INDEX idx_contacts_account_id    ON contacts (account_id);
CREATE INDEX idx_contacts_email         ON contacts (email);
CREATE INDEX idx_contacts_last_name     ON contacts (last_name);
CREATE INDEX idx_contacts_owner_id      ON contacts (owner_id);
CREATE INDEX idx_contacts_custom_fields ON contacts USING GIN (custom_fields);

CREATE TRIGGER trg_contacts_set_updated_at
    BEFORE UPDATE ON contacts
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- =============================================================================
-- TABLE: leads
-- =============================================================================
CREATE TABLE leads (
    id                      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sfid                    VARCHAR(40),
    first_name              VARCHAR(100),
    last_name               VARCHAR(100) NOT NULL,
    email                   VARCHAR(255),
    phone                   VARCHAR(40),
    company                 VARCHAR(255) NOT NULL,
    title                   VARCHAR(128),
    status                  VARCHAR(50) NOT NULL DEFAULT 'New',  -- New, Contacted, Qualified, Unqualified, Converted
    lead_source             VARCHAR(100),
    industry                VARCHAR(100),
    converted_at            TIMESTAMPTZ,
    converted_account_id    BIGINT REFERENCES accounts(id),
    converted_contact_id    BIGINT REFERENCES contacts(id),
    custom_fields           JSONB NOT NULL DEFAULT '{}'::jsonb,
    owner_id                BIGINT REFERENCES users(id),
    created_by_id           BIGINT REFERENCES users(id),
    updated_by_id           BIGINT REFERENCES users(id),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_deleted              BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at              TIMESTAMPTZ,
    deleted_by_id           BIGINT REFERENCES users(id)
);

CREATE INDEX idx_leads_email         ON leads (email);
CREATE INDEX idx_leads_status        ON leads (status);
CREATE INDEX idx_leads_company       ON leads (company);
CREATE INDEX idx_leads_owner_id      ON leads (owner_id);
CREATE INDEX idx_leads_custom_fields ON leads USING GIN (custom_fields);

CREATE TRIGGER trg_leads_set_updated_at
    BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- =============================================================================
-- TABLE: opportunities
-- =============================================================================
CREATE TABLE opportunities (
    id                      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sfid                    VARCHAR(40),
    name                    VARCHAR(255) NOT NULL,
    account_id              BIGINT REFERENCES accounts(id),
    contact_id              BIGINT REFERENCES contacts(id),
    stage                   VARCHAR(100) NOT NULL DEFAULT 'Prospecting',
    probability             INTEGER CHECK (probability >= 0 AND probability <= 100),
    amount                  NUMERIC(18, 2),
    close_date              DATE NOT NULL,
    type                    VARCHAR(100),
    lead_source             VARCHAR(100),
    next_step               VARCHAR(255),
    description             TEXT,
    is_won                  BOOLEAN NOT NULL DEFAULT FALSE,
    is_closed               BOOLEAN NOT NULL DEFAULT FALSE,
    closed_at               TIMESTAMPTZ,
    custom_fields           JSONB NOT NULL DEFAULT '{}'::jsonb,
    owner_id                BIGINT REFERENCES users(id),
    created_by_id           BIGINT REFERENCES users(id),
    updated_by_id           BIGINT REFERENCES users(id),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_deleted              BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at              TIMESTAMPTZ,
    deleted_by_id           BIGINT REFERENCES users(id)
);

CREATE INDEX idx_opportunities_account_id     ON opportunities (account_id);
CREATE INDEX idx_opportunities_stage          ON opportunities (stage);
CREATE INDEX idx_opportunities_close_date     ON opportunities (close_date);
CREATE INDEX idx_opportunities_owner_id       ON opportunities (owner_id);
CREATE INDEX idx_opportunities_custom_fields  ON opportunities USING GIN (custom_fields);

CREATE TRIGGER trg_opportunities_set_updated_at
    BEFORE UPDATE ON opportunities
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- =============================================================================
-- TABLE: cases
-- =============================================================================
CREATE TABLE cases (
    id                      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sfid                    VARCHAR(40),
    case_number             VARCHAR(30),
    account_id              BIGINT REFERENCES accounts(id),
    contact_id              BIGINT REFERENCES contacts(id),
    subject                 VARCHAR(255) NOT NULL,
    description             TEXT,
    status                  VARCHAR(100) NOT NULL DEFAULT 'New',
    priority                VARCHAR(50) NOT NULL DEFAULT 'Medium',
    origin                  VARCHAR(100),
    type                    VARCHAR(100),
    reason                  VARCHAR(255),
    closed_at               TIMESTAMPTZ,
    custom_fields           JSONB NOT NULL DEFAULT '{}'::jsonb,
    owner_id                BIGINT REFERENCES users(id),
    created_by_id           BIGINT REFERENCES users(id),
    updated_by_id           BIGINT REFERENCES users(id),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_deleted              BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at              TIMESTAMPTZ,
    deleted_by_id           BIGINT REFERENCES users(id),
    CONSTRAINT uq_cases_case_number UNIQUE (case_number)
);

CREATE INDEX idx_cases_account_id      ON cases (account_id);
CREATE INDEX idx_cases_contact_id      ON cases (contact_id);
CREATE INDEX idx_cases_status          ON cases (status);
CREATE INDEX idx_cases_priority        ON cases (priority);
CREATE INDEX idx_cases_owner_id        ON cases (owner_id);
CREATE INDEX idx_cases_custom_fields   ON cases USING GIN (custom_fields);

CREATE TRIGGER trg_cases_set_updated_at
    BEFORE UPDATE ON cases
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- =============================================================================
-- TABLE: custom_field_definitions
-- =============================================================================
CREATE TABLE custom_field_definitions (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sfid            VARCHAR(40),
    object_name     VARCHAR(100) NOT NULL,   -- e.g. 'accounts', 'contacts'
    field_name      VARCHAR(100) NOT NULL,
    field_label     VARCHAR(255),
    field_type      VARCHAR(50) NOT NULL,    -- Text, Number, Date, DateTime, Boolean, Picklist, MultiPicklist, Email, URL, TextArea, Currency
    is_required     BOOLEAN NOT NULL DEFAULT FALSE,
    default_value   TEXT,
    picklist_values JSONB,
    field_order     INTEGER,
    description     TEXT,
    custom_fields   JSONB NOT NULL DEFAULT '{}'::jsonb,
    owner_id        BIGINT REFERENCES users(id),
    created_by_id   BIGINT REFERENCES users(id),
    updated_by_id   BIGINT REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_deleted      BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at      TIMESTAMPTZ,
    deleted_by_id   BIGINT REFERENCES users(id),
    CONSTRAINT uq_custom_field_definitions_object_field UNIQUE (object_name, field_name)
);

CREATE INDEX idx_custom_field_definitions_object_name   ON custom_field_definitions (object_name);
CREATE INDEX idx_custom_field_definitions_owner_id      ON custom_field_definitions (owner_id);
CREATE INDEX idx_custom_field_definitions_custom_fields ON custom_field_definitions USING GIN (custom_fields);

CREATE TRIGGER trg_custom_field_definitions_set_updated_at
    BEFORE UPDATE ON custom_field_definitions
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

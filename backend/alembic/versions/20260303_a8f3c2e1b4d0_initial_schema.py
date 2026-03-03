"""Initial schema: users, accounts, contacts, leads, custom_field_definitions

Revision ID: a8f3c2e1b4d0
Revises:
Create Date: 2026-03-03 00:00:00.000000+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a8f3c2e1b4d0"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ---------------------------------------------------------------------------
    # Trigger function: auto-set updated_at on every UPDATE
    # ---------------------------------------------------------------------------
    op.execute(
        """
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    # ---------------------------------------------------------------------------
    # TABLE: users
    # ---------------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("sfid", sa.String(40), nullable=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("custom_fields", postgresql.JSONB(), nullable=False, server_default="{}"),
        # Self-referential FKs added via ALTER TABLE below (after table creation)
        sa.Column("owner_id", sa.BigInteger(), nullable=True),
        sa.Column("created_by_id", sa.BigInteger(), nullable=True),
        sa.Column("updated_by_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("deleted_by_id", sa.BigInteger(), nullable=True),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    # Self-referential foreign keys
    op.create_foreign_key("fk_users_owner_id", "users", "users", ["owner_id"], ["id"])
    op.create_foreign_key("fk_users_created_by_id", "users", "users", ["created_by_id"], ["id"])
    op.create_foreign_key("fk_users_updated_by_id", "users", "users", ["updated_by_id"], ["id"])
    op.create_foreign_key("fk_users_deleted_by_id", "users", "users", ["deleted_by_id"], ["id"])

    op.create_index("idx_users_email", "users", ["email"])
    op.create_index("idx_users_owner_id", "users", ["owner_id"])
    op.create_index(
        "idx_users_custom_fields",
        "users",
        [sa.text("custom_fields")],
        postgresql_using="gin",
    )

    op.execute(
        """
        CREATE TRIGGER trg_users_set_updated_at
            BEFORE UPDATE ON users
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )

    # ---------------------------------------------------------------------------
    # TABLE: accounts
    # ---------------------------------------------------------------------------
    op.create_table(
        "accounts",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("sfid", sa.String(40), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(50), nullable=True),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("website", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(40), nullable=True),
        sa.Column("billing_street", sa.String(255), nullable=True),
        sa.Column("billing_city", sa.String(100), nullable=True),
        sa.Column("billing_state", sa.String(100), nullable=True),
        sa.Column("billing_postal_code", sa.String(20), nullable=True),
        sa.Column("billing_country", sa.String(100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("annual_revenue", sa.Numeric(18, 2), nullable=True),
        sa.Column("number_of_employees", sa.Integer(), nullable=True),
        sa.Column("custom_fields", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("owner_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_by_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("deleted_by_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("idx_accounts_name", "accounts", ["name"])
    op.create_index("idx_accounts_owner_id", "accounts", ["owner_id"])
    op.create_index(
        "idx_accounts_custom_fields",
        "accounts",
        [sa.text("custom_fields")],
        postgresql_using="gin",
    )

    op.execute(
        """
        CREATE TRIGGER trg_accounts_set_updated_at
            BEFORE UPDATE ON accounts
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )

    # ---------------------------------------------------------------------------
    # TABLE: contacts
    # ---------------------------------------------------------------------------
    op.create_table(
        "contacts",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("sfid", sa.String(40), nullable=True),
        sa.Column("account_id", sa.BigInteger(), sa.ForeignKey("accounts.id"), nullable=True),
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(40), nullable=True),
        sa.Column("mobile_phone", sa.String(40), nullable=True),
        sa.Column("title", sa.String(128), nullable=True),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("mailing_street", sa.String(255), nullable=True),
        sa.Column("mailing_city", sa.String(100), nullable=True),
        sa.Column("mailing_state", sa.String(100), nullable=True),
        sa.Column("mailing_postal_code", sa.String(20), nullable=True),
        sa.Column("mailing_country", sa.String(100), nullable=True),
        sa.Column("custom_fields", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("owner_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_by_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("deleted_by_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("idx_contacts_account_id", "contacts", ["account_id"])
    op.create_index("idx_contacts_email", "contacts", ["email"])
    op.create_index("idx_contacts_last_name", "contacts", ["last_name"])
    op.create_index("idx_contacts_owner_id", "contacts", ["owner_id"])
    op.create_index(
        "idx_contacts_custom_fields",
        "contacts",
        [sa.text("custom_fields")],
        postgresql_using="gin",
    )

    op.execute(
        """
        CREATE TRIGGER trg_contacts_set_updated_at
            BEFORE UPDATE ON contacts
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )

    # ---------------------------------------------------------------------------
    # TABLE: leads
    # ---------------------------------------------------------------------------
    op.create_table(
        "leads",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("sfid", sa.String(40), nullable=True),
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(40), nullable=True),
        sa.Column("company", sa.String(255), nullable=False),
        sa.Column("title", sa.String(128), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="New"),
        sa.Column("lead_source", sa.String(100), nullable=True),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("converted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("converted_account_id", sa.BigInteger(), sa.ForeignKey("accounts.id"), nullable=True),
        sa.Column("converted_contact_id", sa.BigInteger(), sa.ForeignKey("contacts.id"), nullable=True),
        sa.Column("custom_fields", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("owner_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_by_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("deleted_by_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("idx_leads_email", "leads", ["email"])
    op.create_index("idx_leads_status", "leads", ["status"])
    op.create_index("idx_leads_company", "leads", ["company"])
    op.create_index("idx_leads_owner_id", "leads", ["owner_id"])
    op.create_index(
        "idx_leads_custom_fields",
        "leads",
        [sa.text("custom_fields")],
        postgresql_using="gin",
    )

    op.execute(
        """
        CREATE TRIGGER trg_leads_set_updated_at
            BEFORE UPDATE ON leads
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )

    # ---------------------------------------------------------------------------
    # TABLE: custom_field_definitions
    # ---------------------------------------------------------------------------
    op.create_table(
        "custom_field_definitions",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("sfid", sa.String(40), nullable=True),
        sa.Column("object_name", sa.String(100), nullable=False),
        sa.Column("field_name", sa.String(100), nullable=False),
        sa.Column("field_label", sa.String(255), nullable=True),
        sa.Column("field_type", sa.String(50), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("default_value", sa.Text(), nullable=True),
        sa.Column("picklist_values", postgresql.JSONB(), nullable=True),
        sa.Column("field_order", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("custom_fields", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("owner_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_by_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("deleted_by_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True),
        sa.UniqueConstraint("object_name", "field_name", name="uq_custom_field_definitions_object_field"),
    )
    op.create_index("idx_custom_field_definitions_object_name", "custom_field_definitions", ["object_name"])
    op.create_index("idx_custom_field_definitions_owner_id", "custom_field_definitions", ["owner_id"])
    op.create_index(
        "idx_custom_field_definitions_custom_fields",
        "custom_field_definitions",
        [sa.text("custom_fields")],
        postgresql_using="gin",
    )

    op.execute(
        """
        CREATE TRIGGER trg_custom_field_definitions_set_updated_at
            BEFORE UPDATE ON custom_field_definitions
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_custom_field_definitions_set_updated_at ON custom_field_definitions")
    op.drop_table("custom_field_definitions")

    op.execute("DROP TRIGGER IF EXISTS trg_leads_set_updated_at ON leads")
    op.drop_table("leads")

    op.execute("DROP TRIGGER IF EXISTS trg_contacts_set_updated_at ON contacts")
    op.drop_table("contacts")

    op.execute("DROP TRIGGER IF EXISTS trg_accounts_set_updated_at ON accounts")
    op.drop_table("accounts")

    op.execute("DROP TRIGGER IF EXISTS trg_users_set_updated_at ON users")
    # Drop self-referential FKs before dropping the table
    op.drop_constraint("fk_users_deleted_by_id", "users", type_="foreignkey")
    op.drop_constraint("fk_users_updated_by_id", "users", type_="foreignkey")
    op.drop_constraint("fk_users_created_by_id", "users", type_="foreignkey")
    op.drop_constraint("fk_users_owner_id", "users", type_="foreignkey")
    op.drop_table("users")

    op.execute("DROP FUNCTION IF EXISTS set_updated_at()")

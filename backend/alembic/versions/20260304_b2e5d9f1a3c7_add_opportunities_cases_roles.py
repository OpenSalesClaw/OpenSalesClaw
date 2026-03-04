"""Add opportunities, cases, and roles tables; add role_id to users

Revision ID: b2e5d9f1a3c7
Revises: a8f3c2e1b4d0
Create Date: 2026-03-04 00:00:00.000000+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2e5d9f1a3c7"
down_revision: str | None = "a8f3c2e1b4d0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ---------------------------------------------------------------------------
    # TABLE: roles
    # ---------------------------------------------------------------------------
    op.create_table(
        "roles",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("sfid", sa.String(40), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("parent_role_id", sa.BigInteger(), nullable=True),
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
        sa.UniqueConstraint("name", name="uq_roles_name"),
    )
    # Self-referential FK for parent_role_id
    op.create_foreign_key("fk_roles_parent_role_id", "roles", "roles", ["parent_role_id"], ["id"])

    op.create_index("idx_roles_parent_role_id", "roles", ["parent_role_id"])
    op.create_index("idx_roles_owner_id", "roles", ["owner_id"])
    op.create_index(
        "idx_roles_custom_fields",
        "roles",
        [sa.text("custom_fields")],
        postgresql_using="gin",
    )

    op.execute(
        """
        CREATE TRIGGER trg_roles_set_updated_at
            BEFORE UPDATE ON roles
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )

    # ---------------------------------------------------------------------------
    # Add role_id to users
    # ---------------------------------------------------------------------------
    op.add_column("users", sa.Column("role_id", sa.BigInteger(), nullable=True))
    op.create_foreign_key("fk_users_role_id", "users", "roles", ["role_id"], ["id"])
    op.create_index("idx_users_role_id", "users", ["role_id"])

    # ---------------------------------------------------------------------------
    # TABLE: opportunities
    # ---------------------------------------------------------------------------
    op.create_table(
        "opportunities",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("sfid", sa.String(40), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("account_id", sa.BigInteger(), sa.ForeignKey("accounts.id"), nullable=True),
        sa.Column("contact_id", sa.BigInteger(), sa.ForeignKey("contacts.id"), nullable=True),
        sa.Column("stage", sa.String(100), nullable=False, server_default="Prospecting"),
        sa.Column(
            "probability",
            sa.Integer(),
            sa.CheckConstraint("probability >= 0 AND probability <= 100", name="ck_opportunities_probability"),
            nullable=True,
        ),
        sa.Column("amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("close_date", sa.Date(), nullable=False),
        sa.Column("type", sa.String(100), nullable=True),
        sa.Column("lead_source", sa.String(100), nullable=True),
        sa.Column("next_step", sa.String(255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_won", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_closed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("closed_at", sa.TIMESTAMP(timezone=True), nullable=True),
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
    op.create_index("idx_opportunities_account_id", "opportunities", ["account_id"])
    op.create_index("idx_opportunities_stage", "opportunities", ["stage"])
    op.create_index("idx_opportunities_close_date", "opportunities", ["close_date"])
    op.create_index("idx_opportunities_owner_id", "opportunities", ["owner_id"])
    op.create_index(
        "idx_opportunities_custom_fields",
        "opportunities",
        [sa.text("custom_fields")],
        postgresql_using="gin",
    )

    op.execute(
        """
        CREATE TRIGGER trg_opportunities_set_updated_at
            BEFORE UPDATE ON opportunities
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )

    # ---------------------------------------------------------------------------
    # TABLE: cases
    # ---------------------------------------------------------------------------
    op.create_table(
        "cases",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("sfid", sa.String(40), nullable=True),
        sa.Column("case_number", sa.String(30), nullable=True),
        sa.Column("account_id", sa.BigInteger(), sa.ForeignKey("accounts.id"), nullable=True),
        sa.Column("contact_id", sa.BigInteger(), sa.ForeignKey("contacts.id"), nullable=True),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(100), nullable=False, server_default="New"),
        sa.Column("priority", sa.String(50), nullable=False, server_default="Medium"),
        sa.Column("origin", sa.String(100), nullable=True),
        sa.Column("type", sa.String(100), nullable=True),
        sa.Column("reason", sa.String(255), nullable=True),
        sa.Column("closed_at", sa.TIMESTAMP(timezone=True), nullable=True),
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
        sa.UniqueConstraint("case_number", name="uq_cases_case_number"),
    )
    op.create_index("idx_cases_account_id", "cases", ["account_id"])
    op.create_index("idx_cases_contact_id", "cases", ["contact_id"])
    op.create_index("idx_cases_status", "cases", ["status"])
    op.create_index("idx_cases_priority", "cases", ["priority"])
    op.create_index("idx_cases_owner_id", "cases", ["owner_id"])
    op.create_index(
        "idx_cases_custom_fields",
        "cases",
        [sa.text("custom_fields")],
        postgresql_using="gin",
    )

    op.execute(
        """
        CREATE TRIGGER trg_cases_set_updated_at
            BEFORE UPDATE ON cases
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_cases_set_updated_at ON cases")
    op.drop_table("cases")

    op.execute("DROP TRIGGER IF EXISTS trg_opportunities_set_updated_at ON opportunities")
    op.drop_table("opportunities")

    op.drop_index("idx_users_role_id", table_name="users")
    op.drop_constraint("fk_users_role_id", "users", type_="foreignkey")
    op.drop_column("users", "role_id")

    op.execute("DROP TRIGGER IF EXISTS trg_roles_set_updated_at ON roles")
    op.drop_constraint("fk_roles_parent_role_id", "roles", type_="foreignkey")
    op.drop_table("roles")

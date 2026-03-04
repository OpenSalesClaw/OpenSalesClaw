"""Add custom_objects and custom_object_records tables

Revision ID: d4a7b0c5e6f9
Revises: c3f6e0a2b1d8
Create Date: 2026-03-04 12:00:00.000000+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d4a7b0c5e6f9"
down_revision: str | None = "c3f6e0a2b1d8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ---------------------------------------------------------------------------
    # TABLE: custom_objects
    # ---------------------------------------------------------------------------
    op.create_table(
        "custom_objects",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("sfid", sa.String(40), nullable=True),
        sa.Column("api_name", sa.String(100), nullable=False),
        sa.Column("label", sa.String(255), nullable=False),
        sa.Column("plural_label", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon_name", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("custom_fields", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("owner_id", sa.BigInteger(), nullable=True),
        sa.Column("created_by_id", sa.BigInteger(), nullable=True),
        sa.Column("updated_by_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("deleted_by_id", sa.BigInteger(), nullable=True),
    )
    op.create_index("idx_custom_objects_api_name", "custom_objects", ["api_name"], unique=True)
    op.create_index("idx_custom_objects_custom_fields", "custom_objects", ["custom_fields"], postgresql_using="gin")

    # FK constraints
    op.create_foreign_key(None, "custom_objects", "users", ["owner_id"], ["id"])
    op.create_foreign_key(None, "custom_objects", "users", ["created_by_id"], ["id"])
    op.create_foreign_key(None, "custom_objects", "users", ["updated_by_id"], ["id"])
    op.create_foreign_key(None, "custom_objects", "users", ["deleted_by_id"], ["id"])

    # updated_at trigger
    op.execute(
        """
        CREATE TRIGGER set_updated_at_custom_objects
        BEFORE UPDATE ON custom_objects
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )

    # ---------------------------------------------------------------------------
    # TABLE: custom_object_records
    # ---------------------------------------------------------------------------
    op.create_table(
        "custom_object_records",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("sfid", sa.String(40), nullable=True),
        sa.Column("custom_object_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("data", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("custom_fields", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("owner_id", sa.BigInteger(), nullable=True),
        sa.Column("created_by_id", sa.BigInteger(), nullable=True),
        sa.Column("updated_by_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("deleted_by_id", sa.BigInteger(), nullable=True),
    )
    op.create_index("idx_custom_object_records_custom_object_id", "custom_object_records", ["custom_object_id"])
    op.create_index("idx_custom_object_records_name", "custom_object_records", ["name"])
    op.create_index("idx_custom_object_records_data", "custom_object_records", ["data"], postgresql_using="gin")
    op.create_index(
        "idx_custom_object_records_custom_fields",
        "custom_object_records",
        ["custom_fields"],
        postgresql_using="gin",
    )

    # FK constraints
    op.create_foreign_key(None, "custom_object_records", "custom_objects", ["custom_object_id"], ["id"])
    op.create_foreign_key(None, "custom_object_records", "users", ["owner_id"], ["id"])
    op.create_foreign_key(None, "custom_object_records", "users", ["created_by_id"], ["id"])
    op.create_foreign_key(None, "custom_object_records", "users", ["updated_by_id"], ["id"])
    op.create_foreign_key(None, "custom_object_records", "users", ["deleted_by_id"], ["id"])

    # updated_at trigger
    op.execute(
        """
        CREATE TRIGGER set_updated_at_custom_object_records
        BEFORE UPDATE ON custom_object_records
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS set_updated_at_custom_object_records ON custom_object_records")
    op.execute("DROP TRIGGER IF EXISTS set_updated_at_custom_objects ON custom_objects")
    op.drop_table("custom_object_records")
    op.drop_table("custom_objects")

"""Add case_number_seq PostgreSQL sequence

Replaces the MAX()+1 race-condition approach in CaseService with a proper
PostgreSQL sequence.  The sequence is also referenced from the SQLAlchemy
model metadata so that ``Base.metadata.create_all`` (used in tests) creates
it automatically.

Revision ID: c3f6e0a2b1d8
Revises: b2e5d9f1a3c7
Create Date: 2026-03-04 00:00:00.000000+00:00

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3f6e0a2b1d8"
down_revision: str | None = "b2e5d9f1a3c7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE SEQUENCE IF NOT EXISTS case_number_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1"
    )
    # Advance the sequence past any existing case numbers to avoid collisions on
    # existing data.  Skip when the table is empty (avoids setval(seq, 0) error).
    op.execute(
        """
        DO $$
        DECLARE
            max_num integer;
        BEGIN
            SELECT MAX(CAST(SPLIT_PART(case_number, '-', 2) AS INTEGER))
            INTO max_num
            FROM cases
            WHERE case_number ~ '^CS-[0-9]+$';

            IF max_num IS NOT NULL THEN
                PERFORM setval('case_number_seq', max_num);
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP SEQUENCE IF EXISTS case_number_seq")

"""create set_updated_at trigger function and attach to edge tables

Revision ID: a006_updated_at_trigger
Revises: a005_snapshot_tables
Create Date: 2026-03-14

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a006_updated_at_trigger'
down_revision: str | Sequence[str] | None = 'a005_snapshot_tables'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TRIGGER_FUNCTION = """
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

DROP_TRIGGER_FUNCTION = "DROP FUNCTION IF EXISTS set_updated_at();"

TABLES_WITH_TRIGGER = [
    'actor_project_edges',
    'actor_actor_edges',
]


def upgrade() -> None:
    """Create set_updated_at() function and attach trigger to edge tables."""
    op.execute(TRIGGER_FUNCTION)

    for table in TABLES_WITH_TRIGGER:
        op.execute(f"""
            CREATE TRIGGER trg_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION set_updated_at();
        """)


def downgrade() -> None:
    """Drop triggers and function."""
    for table in reversed(TABLES_WITH_TRIGGER):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_updated_at ON {table};")

    op.execute(DROP_TRIGGER_FUNCTION)

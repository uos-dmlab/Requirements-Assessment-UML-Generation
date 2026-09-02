"""Add diagram_type column to runs table.

Revision ID: 20250225_add_diagram_type
Revises: 20250212_redesign_runs
"""

from alembic import op
import sqlalchemy as sa

revision = "20250225_add_diagram_type"
down_revision = "20250212_redesign_runs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "runs",
        sa.Column("diagram_type", sa.String(20), nullable=False, server_default="class"),
    )


def downgrade() -> None:
    op.drop_column("runs", "diagram_type")

"""Add detail_level column to runs table.

Revision ID: 20250226_add_detail_level
Revises: 20250225_add_perf_metrics
"""

from alembic import op
import sqlalchemy as sa

revision = "20250226_add_detail_level"
down_revision = "20250225_add_perf_metrics"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "runs",
        sa.Column("detail_level", sa.String(20), nullable=False, server_default="domain"),
    )


def downgrade() -> None:
    op.drop_column("runs", "detail_level")

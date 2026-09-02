"""Add performance metrics columns to runs table.

Revision ID: 20250225_add_perf_metrics
Revises: 20250225_add_diagram_type
"""

from alembic import op
import sqlalchemy as sa

revision = "20250225_add_perf_metrics"
down_revision = "20250225_add_diagram_type"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("runs", sa.Column("validation_time_ms", sa.Integer(), nullable=True))
    op.add_column("runs", sa.Column("generation_time_ms", sa.Integer(), nullable=True))
    op.add_column("runs", sa.Column("refine_iterations", sa.Integer(), nullable=True))
    op.add_column("runs", sa.Column("syntax_valid", sa.Boolean(), nullable=True))
    op.add_column("runs", sa.Column("llm_calls_count", sa.Integer(), nullable=True))
    op.add_column("runs", sa.Column("tokens_used", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("runs", "tokens_used")
    op.drop_column("runs", "llm_calls_count")
    op.drop_column("runs", "syntax_valid")
    op.drop_column("runs", "refine_iterations")
    op.drop_column("runs", "generation_time_ms")
    op.drop_column("runs", "validation_time_ms")

"""Redesign runs table — iterative workspace model.

Drop run_results table, rebuild runs with new schema.

Revision ID: 20250212_redesign_runs
Revises: 20250203_projects_runs
"""

from alembic import op
import sqlalchemy as sa

revision = '20250212_redesign_runs'
down_revision = '20250203_projects_runs'
branch_labels = None
depends_on = None


def upgrade():
    # Drop old tables
    op.drop_table('run_results')

    # Drop old runs columns and add new ones
    # Easiest approach: drop and recreate
    op.drop_table('artifacts')
    op.drop_table('runs')

    # Recreate runs with new schema
    op.create_table(
        'runs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),

        # Requirements
        sa.Column('requirements_text', sa.Text(), default=''),
        sa.Column('requirements_updated_at', sa.DateTime(timezone=True), nullable=True),

        # Validation
        sa.Column('validation_status', sa.String(20), nullable=True),
        sa.Column('validation_score', sa.Integer(), nullable=True),
        sa.Column('validation_result', sa.JSON(), nullable=True),
        sa.Column('validated_at', sa.DateTime(timezone=True), nullable=True),

        # Generation
        sa.Column('generation_status', sa.String(20), nullable=True),
        sa.Column('diagram_data', sa.JSON(), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=True),

        # Metadata
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Recreate artifacts
    op.create_table(
        'artifacts',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('run_id', sa.Integer(), sa.ForeignKey('runs.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('kind', sa.String(50), nullable=False),
        sa.Column('content_type', sa.String(100), nullable=False),
        sa.Column('filename', sa.String(255), nullable=True),
        sa.Column('data', sa.LargeBinary(), nullable=True),
        sa.Column('storage_path', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('artifacts')
    op.drop_table('runs')
    # Can't fully restore old schema, would need manual recreation

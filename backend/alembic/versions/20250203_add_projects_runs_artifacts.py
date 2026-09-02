"""Add projects, runs, and artifacts tables

Revision ID: 20250203_projects_runs
Revises: 20250126_auth_schema
Create Date: 2025-02-03

Changes:
- Create projects table
- Create requirements_drafts table
- Create runs table
- Create run_results table
- Create artifacts table
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250203_projects_runs'
down_revision: Union[str, None] = '20250126_auth_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # === PROJECTS TABLE ===
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_projects_id', 'projects', ['id'])
    op.create_index('ix_projects_user_id', 'projects', ['user_id'])

    # === REQUIREMENTS_DRAFTS TABLE ===
    op.create_table(
        'requirements_drafts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False, server_default=''),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id')
    )
    op.create_index('ix_requirements_drafts_id', 'requirements_drafts', ['id'])
    op.create_index('ix_requirements_drafts_project_id', 'requirements_drafts', ['project_id'])

    # === RUNS TABLE ===
    op.create_table(
        'runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('kind', sa.String(30), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='queued'),
        sa.Column('progress', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('requirements_snapshot_text', sa.Text(), nullable=True),
        sa.Column('requirements_char_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('score_value', sa.Integer(), nullable=True),
        sa.Column('score_max', sa.Integer(), nullable=True, server_default='60'),
        sa.Column('has_diagram', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_runs_id', 'runs', ['id'])
    op.create_index('ix_runs_project_id', 'runs', ['project_id'])

    # === RUN_RESULTS TABLE ===
    op.create_table(
        'run_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('run_id', sa.Integer(), nullable=False),
        sa.Column('metrics', sa.JSON(), nullable=True),
        sa.Column('ai_feedback', sa.JSON(), nullable=True),
        sa.Column('summary_badge', sa.JSON(), nullable=True),
        sa.Column('plantuml_source', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['run_id'], ['runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('run_id')
    )
    op.create_index('ix_run_results_id', 'run_results', ['id'])
    op.create_index('ix_run_results_run_id', 'run_results', ['run_id'])

    # === ARTIFACTS TABLE ===
    op.create_table(
        'artifacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('run_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('kind', sa.String(50), nullable=False),
        sa.Column('content_type', sa.String(100), nullable=False),
        sa.Column('filename', sa.String(255), nullable=True),
        sa.Column('data', sa.LargeBinary(), nullable=True),
        sa.Column('storage_path', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['run_id'], ['runs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_artifacts_id', 'artifacts', ['id'])
    op.create_index('ix_artifacts_run_id', 'artifacts', ['run_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_artifacts_run_id', table_name='artifacts')
    op.drop_index('ix_artifacts_id', table_name='artifacts')
    op.drop_table('artifacts')

    op.drop_index('ix_run_results_run_id', table_name='run_results')
    op.drop_index('ix_run_results_id', table_name='run_results')
    op.drop_table('run_results')

    op.drop_index('ix_runs_project_id', table_name='runs')
    op.drop_index('ix_runs_id', table_name='runs')
    op.drop_table('runs')

    op.drop_index('ix_requirements_drafts_project_id', table_name='requirements_drafts')
    op.drop_index('ix_requirements_drafts_id', table_name='requirements_drafts')
    op.drop_table('requirements_drafts')

    op.drop_index('ix_projects_user_id', table_name='projects')
    op.drop_index('ix_projects_id', table_name='projects')
    op.drop_table('projects')

"""Add version and session_id to diagrams

Revision ID: 20250109_add_version_session
Revises: 1255985ee36c
Create Date: 2025-01-09 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250109_add_version_session'
down_revision: Union[str, None] = '1255985ee36c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add version column to diagrams table
    op.add_column('diagrams', sa.Column('version', sa.Integer(), nullable=False, server_default='1'))
    
    # Add session_id column to diagrams table
    op.add_column('diagrams', sa.Column('session_id', sa.String(), nullable=True))
    
    # Add foreign key constraint for session_id
    op.create_foreign_key('fk_diagrams_session_id', 'diagrams', 'requirement_sessions', ['session_id'], ['id'])
    
    # Add index for better performance on session_id queries
    op.create_index('idx_diagrams_session_id', 'diagrams', ['session_id'])
    
    # Add index for version queries
    op.create_index('idx_diagrams_version', 'diagrams', ['version'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('idx_diagrams_version', table_name='diagrams')
    op.drop_index('idx_diagrams_session_id', table_name='diagrams')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_diagrams_session_id', 'diagrams', type_='foreignkey')
    
    # Drop columns
    op.drop_column('diagrams', 'session_id')
    op.drop_column('diagrams', 'version')


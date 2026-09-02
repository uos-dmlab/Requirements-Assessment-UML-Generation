"""Remove version field from diagrams table

Revision ID: 20250109_remove_version
Revises: 20250109_add_version_session
Create Date: 2025-01-09 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250109_remove_version'
down_revision: Union[str, None] = '20250109_add_version_session'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop version-related indexes
    op.drop_index('idx_diagrams_version', table_name='diagrams')
    
    # Drop version column
    op.drop_column('diagrams', 'version')


def downgrade() -> None:
    """Downgrade schema."""
    # Add version column back
    op.add_column('diagrams', sa.Column('version', sa.Integer(), nullable=False, server_default='1'))
    
    # Add version index back
    op.create_index('idx_diagrams_version', 'diagrams', ['version'])

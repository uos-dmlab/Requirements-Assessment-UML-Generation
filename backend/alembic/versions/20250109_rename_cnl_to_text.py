"""Rename cnl_text to text in requirement_messages

Revision ID: 20250109_rename_cnl_text
Revises: 20250109_remove_version
Create Date: 2025-01-09 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250109_rename_cnl_text'
down_revision: Union[str, None] = '20250109_remove_version'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename cnl_text column to text
    op.alter_column('requirement_messages', 'cnl_text', new_column_name='text')


def downgrade() -> None:
    """Downgrade schema."""
    # Rename text column back to cnl_text
    op.alter_column('requirement_messages', 'text', new_column_name='cnl_text')

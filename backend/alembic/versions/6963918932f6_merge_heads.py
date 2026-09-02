"""merge heads

Revision ID: 6963918932f6
Revises: d36795a87386, 20250109_rename_cnl_text
Create Date: 2025-09-17 15:40:59.272205

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6963918932f6'
down_revision: Union[str, None] = ('d36795a87386', '20250109_rename_cnl_text')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

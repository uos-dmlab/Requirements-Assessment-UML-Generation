"""merge heads

Revision ID: d36795a87386
Revises: 1255985ee36c
Create Date: 2025-09-09 13:48:02.714451

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd36795a87386'
down_revision: Union[str, None] = '1255985ee36c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

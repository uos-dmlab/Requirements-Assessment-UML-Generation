"""Auth schema updates for complete authentication API

Revision ID: 20250126_auth_schema
Revises: 6963918932f6
Create Date: 2025-01-26

Changes:
- users: Add full_name, email_verified, auth_provider, created_at, updated_at
- users: Make hashed_password nullable (for OAuth users)
- refresh_tokens: Rename token to token_hash, add revoked_at, user_agent, ip_address
- Create password_reset_tokens table
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250126_auth_schema'
down_revision: Union[str, None] = '6963918932f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # === USERS TABLE UPDATES ===

    # Add new columns to users table
    op.add_column('users', sa.Column('full_name', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('users', sa.Column('auth_provider', sa.String(20), nullable=True, server_default='password'))
    op.add_column('users', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True))

    # Make hashed_password nullable for OAuth users
    op.alter_column('users', 'hashed_password',
                    existing_type=sa.String(),
                    nullable=True)

    # Update existing records to have default auth_provider
    op.execute("UPDATE users SET auth_provider = 'password' WHERE auth_provider IS NULL")
    op.execute("UPDATE users SET email_verified = false WHERE email_verified IS NULL")

    # === REFRESH_TOKENS TABLE UPDATES ===

    # Rename token column to token_hash
    op.alter_column('refresh_tokens', 'token',
                    new_column_name='token_hash',
                    existing_type=sa.String(),
                    nullable=False)

    # Drop the unique constraint on token (now token_hash)
    # Note: The constraint name may vary, adjust if needed
    try:
        op.drop_constraint('refresh_tokens_token_key', 'refresh_tokens', type_='unique')
    except Exception:
        pass  # Constraint may not exist or have different name

    # Add index on token_hash
    op.create_index('ix_refresh_tokens_token_hash', 'refresh_tokens', ['token_hash'])

    # Add new columns
    op.add_column('refresh_tokens', sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('refresh_tokens', sa.Column('user_agent', sa.String(), nullable=True))
    op.add_column('refresh_tokens', sa.Column('ip_address', sa.String(45), nullable=True))

    # Make user_id non-nullable
    op.alter_column('refresh_tokens', 'user_id',
                    existing_type=sa.Integer(),
                    nullable=False)

    # Update created_at to use timezone
    op.alter_column('refresh_tokens', 'created_at',
                    existing_type=sa.DateTime(),
                    type_=sa.DateTime(timezone=True),
                    existing_nullable=True,
                    server_default=sa.func.now())

    # Update expires_at to use timezone
    op.alter_column('refresh_tokens', 'expires_at',
                    existing_type=sa.DateTime(),
                    type_=sa.DateTime(timezone=True),
                    existing_nullable=False)

    # === CREATE PASSWORD_RESET_TOKENS TABLE ===

    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token_hash', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_password_reset_tokens_id', 'password_reset_tokens', ['id'])
    op.create_index('ix_password_reset_tokens_token_hash', 'password_reset_tokens', ['token_hash'])


def downgrade() -> None:
    """Downgrade schema."""
    # === DROP PASSWORD_RESET_TOKENS TABLE ===
    op.drop_index('ix_password_reset_tokens_token_hash', table_name='password_reset_tokens')
    op.drop_index('ix_password_reset_tokens_id', table_name='password_reset_tokens')
    op.drop_table('password_reset_tokens')

    # === REVERT REFRESH_TOKENS TABLE ===
    op.drop_column('refresh_tokens', 'ip_address')
    op.drop_column('refresh_tokens', 'user_agent')
    op.drop_column('refresh_tokens', 'revoked_at')
    op.drop_index('ix_refresh_tokens_token_hash', table_name='refresh_tokens')

    # Rename token_hash back to token
    op.alter_column('refresh_tokens', 'token_hash',
                    new_column_name='token',
                    existing_type=sa.String(),
                    nullable=False)

    # Re-add unique constraint
    op.create_unique_constraint('refresh_tokens_token_key', 'refresh_tokens', ['token'])

    # Make user_id nullable again
    op.alter_column('refresh_tokens', 'user_id',
                    existing_type=sa.Integer(),
                    nullable=True)

    # Revert datetime columns
    op.alter_column('refresh_tokens', 'created_at',
                    existing_type=sa.DateTime(timezone=True),
                    type_=sa.DateTime(),
                    existing_nullable=True)

    op.alter_column('refresh_tokens', 'expires_at',
                    existing_type=sa.DateTime(timezone=True),
                    type_=sa.DateTime(),
                    existing_nullable=False)

    # === REVERT USERS TABLE ===
    op.alter_column('users', 'hashed_password',
                    existing_type=sa.String(),
                    nullable=False)

    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'auth_provider')
    op.drop_column('users', 'email_verified')
    op.drop_column('users', 'full_name')

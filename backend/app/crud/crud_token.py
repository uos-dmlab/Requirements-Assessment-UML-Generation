from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from datetime import datetime, timezone
import hashlib
import secrets

from app.db.models.refresh_token import RefreshToken
from app.db.models.password_reset_token import PasswordResetToken


def hash_token(token: str) -> str:
    """Create SHA-256 hash of a token."""
    return hashlib.sha256(token.encode()).hexdigest()


def generate_token() -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(32)



async def create_refresh_token(
    db: AsyncSession,
    user_id: int,
    token: str,
    expires_at: datetime,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None
) -> RefreshToken:
    """Create a refresh token (stores hash only)."""
    db_token = RefreshToken(
        user_id=user_id,
        token_hash=hash_token(token),
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address
    )
    db.add(db_token)
    await db.commit()
    await db.refresh(db_token)
    return db_token


async def get_refresh_token_by_hash(db: AsyncSession, token: str) -> Optional[RefreshToken]:
    """Get refresh token by verifying against hash."""
    token_hash = hash_token(token)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None)
        )
    )
    return result.scalar_one_or_none()


async def revoke_refresh_token(db: AsyncSession, token: str) -> bool:
    """Revoke a refresh token."""
    token_hash = hash_token(token)
    result = await db.execute(
        update(RefreshToken)
        .where(RefreshToken.token_hash == token_hash)
        .values(revoked_at=datetime.now(timezone.utc))
    )
    await db.commit()
    return result.rowcount > 0


async def revoke_all_user_tokens(db: AsyncSession, user_id: int) -> int:
    """Revoke all refresh tokens for a user."""
    result = await db.execute(
        update(RefreshToken)
        .where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None)
        )
        .values(revoked_at=datetime.now(timezone.utc))
    )
    await db.commit()
    return result.rowcount


async def delete_refresh_token(db: AsyncSession, token: str) -> bool:
    """Delete a refresh token (legacy - prefer revoke)."""
    token_hash = hash_token(token)
    result = await db.execute(
        delete(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    await db.commit()
    return result.rowcount > 0


async def cleanup_expired_tokens(db: AsyncSession) -> int:
    """Delete expired refresh tokens (for maintenance)."""
    result = await db.execute(
        delete(RefreshToken).where(
            RefreshToken.expires_at < datetime.now(timezone.utc)
        )
    )
    await db.commit()
    return result.rowcount



async def create_password_reset_token(
    db: AsyncSession,
    user_id: int,
    token: str,
    expires_at: datetime
) -> PasswordResetToken:
    """Create a password reset token (stores hash only)."""
    db_token = PasswordResetToken(
        user_id=user_id,
        token_hash=hash_token(token),
        expires_at=expires_at
    )
    db.add(db_token)
    await db.commit()
    await db.refresh(db_token)
    return db_token


async def get_password_reset_token(
    db: AsyncSession,
    token: str
) -> Optional[PasswordResetToken]:
    """Get password reset token by verifying against hash."""
    token_hash = hash_token(token)
    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > datetime.now(timezone.utc)
        )
    )
    return result.scalar_one_or_none()


async def mark_password_reset_token_used(
    db: AsyncSession,
    token_id: int
) -> None:
    """Mark a password reset token as used."""
    await db.execute(
        update(PasswordResetToken)
        .where(PasswordResetToken.id == token_id)
        .values(used_at=datetime.now(timezone.utc))
    )
    await db.commit()


async def cleanup_expired_password_reset_tokens(db: AsyncSession) -> int:
    """Delete expired password reset tokens (for maintenance)."""
    result = await db.execute(
        delete(PasswordResetToken).where(
            PasswordResetToken.expires_at < datetime.now(timezone.utc)
        )
    )
    await db.commit()
    return result.rowcount

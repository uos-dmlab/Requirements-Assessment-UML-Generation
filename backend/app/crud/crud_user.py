from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Get user by email address."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """Get user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Create a new user with password authentication."""
    hashed_pw = hash_password(user_in.password)
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_pw,
        auth_provider="password",
        email_verified=False
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_oauth_user(
    db: AsyncSession,
    email: str,
    full_name: Optional[str],
    auth_provider: str,
    email_verified: bool = False
) -> User:
    """Create a new user via OAuth (no password)."""
    user = User(
        email=email,
        full_name=full_name,
        hashed_password=None,
        auth_provider=auth_provider,
        email_verified=email_verified
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_password(db: AsyncSession, user: User, new_password: str) -> User:
    """Update user's password."""
    user.hashed_password = hash_password(new_password)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_email_verified(db: AsyncSession, user: User, verified: bool = True) -> User:
    """Update user's email verification status."""
    user.email_verified = verified
    await db.commit()
    await db.refresh(user)
    return user

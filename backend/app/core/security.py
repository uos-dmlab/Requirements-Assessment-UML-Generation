from typing import Optional
from datetime import datetime, timedelta, timezone
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from jose import jwt, JWTError

from app.db.session import get_db
from app.core.config import settings


# OAuth2 scheme - points to the token endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    if not hashed:
        return False
    return pwd_context.verify(plain, hashed)


def create_access_token(
    user_id: int,
    email: str,
    expires_delta: Optional[timedelta] = None
) -> tuple[str, int]:
    """
    Create a JWT access token.

    Returns:
        Tuple of (token, expires_in_seconds)
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    to_encode = {
        "sub": str(user_id),
        "email": email,
        "iat": now,
        "exp": expire,
        "jti": secrets.token_urlsafe(16)  # Unique token ID
    }

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    expires_in = int(expires_delta.total_seconds())

    return encoded_jwt, expires_in


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def generate_refresh_token() -> str:
    """Generate a secure random refresh token."""
    return secrets.token_urlsafe(32)


def get_refresh_token_expiry() -> datetime:
    """Get expiry datetime for refresh token."""
    return datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)


def get_password_reset_expiry() -> datetime:
    """Get expiry datetime for password reset token."""
    return datetime.now(timezone.utc) + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Dependency to get the current authenticated user.

    Raises HTTPException if token is invalid or user not found.
    """
    # Lazy imports to avoid circular dependency
    from app.core.error_handlers import AuthHTTPException
    from app.schemas.errors import AuthErrorCodes
    from app.crud import crud_user

    if token is None:
        raise AuthHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=AuthErrorCodes.UNAUTHORIZED,
            message="Not authenticated"
        )

    payload = decode_access_token(token)
    if payload is None:
        raise AuthHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=AuthErrorCodes.UNAUTHORIZED,
            message="Invalid or expired token"
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise AuthHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=AuthErrorCodes.UNAUTHORIZED,
            message="Invalid token claims"
        )

    try:
        user_id_int = int(user_id)
    except ValueError:
        raise AuthHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=AuthErrorCodes.UNAUTHORIZED,
            message="Invalid token claims"
        )

    user = await crud_user.get_user_by_id(db, user_id_int)
    if user is None:
        raise AuthHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=AuthErrorCodes.UNAUTHORIZED,
            message="User not found"
        )

    return user


async def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Dependency to optionally get the current user.
    Returns None if not authenticated instead of raising an exception.
    """
    if token is None:
        return None

    try:
        return await get_current_user(token, db)
    except Exception:
        return None

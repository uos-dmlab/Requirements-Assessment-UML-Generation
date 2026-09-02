"""
FastAPI dependency injection utilities.

Re-exports auth dependencies from core.security for backward compatibility.
"""

from app.core.security import get_current_user, get_current_user_optional
from app.db.session import get_db

__all__ = ["get_current_user", "get_current_user_optional", "get_db"]

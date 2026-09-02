"""
Unified error response schemas following the API contract.
"""

from typing import Optional
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Unified error detail structure."""
    code: str
    message: str
    fields: Optional[dict[str, str]] = None


class ErrorResponse(BaseModel):
    """Unified error response wrapper."""
    error: ErrorDetail


# Error codes for authentication
class AuthErrorCodes:
    VALIDATION_ERROR = "VALIDATION_ERROR"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    UNAUTHORIZED = "UNAUTHORIZED"
    REFRESH_EXPIRED_OR_INVALID = "REFRESH_EXPIRED_OR_INVALID"
    TOKEN_INVALID_OR_EXPIRED = "TOKEN_INVALID_OR_EXPIRED"
    RATE_LIMITED = "RATE_LIMITED"
    OAUTH_STATE_INVALID = "OAUTH_STATE_INVALID"
    OAUTH_EXCHANGE_FAILED = "OAUTH_EXCHANGE_FAILED"
    OAUTH_NOT_CONFIGURED = "OAUTH_NOT_CONFIGURED"


# Error codes for projects
class ProjectErrorCodes:
    PROJECT_NOT_FOUND = "PROJECT_NOT_FOUND"
    FORBIDDEN = "FORBIDDEN"
    REQUIREMENTS_VERSION_CONFLICT = "REQUIREMENTS_VERSION_CONFLICT"


# Error codes for runs
class RunErrorCodes:
    RUN_NOT_FOUND = "RUN_NOT_FOUND"
    INVALID_RUN_KIND = "INVALID_RUN_KIND"
    RUN_NOT_FINISHED = "RUN_NOT_FINISHED"
    RUN_RESULT_NOT_FOUND = "RUN_RESULT_NOT_FOUND"
    RUN_QUOTA_EXCEEDED = "RUN_QUOTA_EXCEEDED"


# Error codes for artifacts
class ArtifactErrorCodes:
    ARTIFACT_NOT_FOUND = "ARTIFACT_NOT_FOUND"


# Error codes for account
class AccountErrorCodes:
    CONFIRM_TEXT_INVALID = "CONFIRM_TEXT_INVALID"

"""
Exception handlers for unified error responses.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.schemas.errors import AuthErrorCodes


def create_error_response(
    code: str,
    message: str,
    status_code: int,
    fields: dict[str, str] | None = None
) -> JSONResponse:
    """Create a unified error response."""
    content = {
        "error": {
            "code": code,
            "message": message,
        }
    }
    if fields:
        content["error"]["fields"] = fields
    return JSONResponse(status_code=status_code, content=content)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors with unified format."""
    fields = {}
    for error in exc.errors():
        # Get the field name from the location
        loc = error.get("loc", [])
        field_name = str(loc[-1]) if loc else "unknown"
        if field_name == "body":
            continue
        fields[field_name] = error.get("msg", "Invalid value")

    return create_error_response(
        code=AuthErrorCodes.VALIDATION_ERROR,
        message="Validation failed",
        status_code=status.HTTP_400_BAD_REQUEST,
        fields=fields if fields else None
    )


class AuthHTTPException(Exception):
    """Custom exception for auth-specific errors with error codes."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        fields: dict[str, str] | None = None
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.fields = fields
        super().__init__(message)


async def auth_exception_handler(
    request: Request, exc: AuthHTTPException
) -> JSONResponse:
    """Handle custom auth exceptions with unified format."""
    return create_error_response(
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        fields=exc.fields
    )

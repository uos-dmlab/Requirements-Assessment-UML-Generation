"""Account Settings API endpoints."""

from fastapi import APIRouter, Depends, Request, Response, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.project import Project
from app.db.models.refresh_token import RefreshToken
from app.core.security import get_current_user, verify_password
from app.core.error_handlers import AuthHTTPException
from app.schemas.errors import AuthErrorCodes, AccountErrorCodes
from app.schemas.account import (
    ChangePasswordRequest,
    DeleteAccountRequest,
    AccountStatusResponse,
)
from app.crud import crud_user, crud_token
from app.api.endpoints.auth import clear_refresh_cookie, REFRESH_COOKIE_NAME


router = APIRouter()


@router.post(
    "/password/change",
    response_model=AccountStatusResponse,
    summary="Change password",
    description="Change the current user's password.",
    responses={
        200: {"description": "Password changed successfully"},
        400: {"description": "Validation error"},
        401: {"description": "Invalid current password"},
    },
)
async def change_password(
    request_data: ChangePasswordRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Change the current user's password."""
    # Verify current password
    if not current_user.hashed_password:
        raise AuthHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=AuthErrorCodes.INVALID_CREDENTIALS,
            message="Cannot change password for OAuth-only account"
        )

    if not verify_password(request_data.current_password, current_user.hashed_password):
        raise AuthHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=AuthErrorCodes.INVALID_CREDENTIALS,
            message="Current password is incorrect"
        )

    # Update password
    await crud_user.update_user_password(db, current_user, request_data.new_password)

    # Revoke all refresh tokens for security
    await crud_token.revoke_all_user_tokens(db, current_user.id)

    # Clear current refresh cookie
    clear_refresh_cookie(response)

    return AccountStatusResponse(status="ok")


@router.post(
    "/delete",
    response_model=AccountStatusResponse,
    summary="Delete account",
    description="Permanently delete the current user's account and all data.",
    responses={
        200: {"description": "Account deleted successfully"},
        400: {"description": "Invalid confirmation text"},
        401: {"description": "Invalid password"},
    },
)
async def delete_account(
    request_data: DeleteAccountRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete the current user's account and all associated data."""
    # Validate confirmation text
    if request_data.confirm_text != "DELETE":
        raise AuthHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=AccountErrorCodes.CONFIRM_TEXT_INVALID,
            message="Confirmation text must be 'DELETE'"
        )

    # Verify password
    if current_user.hashed_password:
        if not verify_password(request_data.password, current_user.hashed_password):
            raise AuthHTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                code=AuthErrorCodes.INVALID_CREDENTIALS,
                message="Password is incorrect"
            )
    else:
        # OAuth-only user - still need some verification
        # For now, just check that password field is not empty
        if not request_data.password:
            raise AuthHTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                code=AuthErrorCodes.INVALID_CREDENTIALS,
                message="Password verification required"
            )

    # Delete all user data (cascading deletes should handle related entities)
    # Projects, runs, artifacts, etc. will be deleted via CASCADE

    # Revoke all refresh tokens
    await crud_token.revoke_all_user_tokens(db, current_user.id)

    # Delete the user
    await db.delete(current_user)
    await db.commit()

    # Clear refresh cookie
    clear_refresh_cookie(response)

    return AccountStatusResponse(status="deleted")

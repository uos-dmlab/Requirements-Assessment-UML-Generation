"""
Authentication API endpoints.

Implements:
- Sign Up (register)
- Sign In (login)
- Current User (/me)
- Refresh Access Token
- Logout
- Forgot Password
- Reset Password
- Google OAuth
"""

from datetime import datetime, timezone
from typing import Optional
import secrets
import urllib.parse

from fastapi import APIRouter, Depends, Form, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.db.session import get_db
from app.db.models.user import User
from app.crud import crud_user, crud_token
from app.core.config import settings
from app.core.security import (
    verify_password,
    create_access_token,
    get_current_user,
    generate_refresh_token,
    get_refresh_token_expiry,
    get_password_reset_expiry,
)
from app.core.error_handlers import AuthHTTPException
from app.schemas.errors import AuthErrorCodes
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserOut,
    AuthResponse,
    RefreshResponse,
    MeResponse,
    StatusResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    Token,
)


router = APIRouter()

# Cookie settings
REFRESH_COOKIE_NAME = "refresh_token"
REFRESH_COOKIE_PATH = "/api/v1/auth"
OAUTH_STATE_COOKIE_NAME = "oauth_state"


def set_refresh_cookie(response: Response, token: str) -> None:
    """Set the refresh token HttpOnly cookie."""
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path=REFRESH_COOKIE_PATH,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )


def clear_refresh_cookie(response: Response) -> None:
    """Clear the refresh token cookie."""
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path=REFRESH_COOKIE_PATH,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )


def get_client_info(request: Request) -> tuple[Optional[str], Optional[str]]:
    """Extract user agent and IP from request."""
    user_agent = request.headers.get("user-agent")
    # Handle X-Forwarded-For for proxied requests
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        ip_address = forwarded_for.split(",")[0].strip()
    else:
        ip_address = request.client.host if request.client else None
    return user_agent, ip_address


# SIGN UP (Register)

@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password.",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Validation error"},
        409: {"description": "Email already registered"},
    },
)
async def register(
    user_in: UserCreate,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account."""
    # Check if email already exists
    existing = await crud_user.get_user_by_email(db, user_in.email)
    if existing:
        raise AuthHTTPException(
            status_code=status.HTTP_409_CONFLICT,
            code=AuthErrorCodes.EMAIL_ALREADY_EXISTS,
            message="A user with this email already exists",
        )

    # Create user
    user = await crud_user.create_user(db, user_in)

    # Generate tokens
    access_token, expires_in = create_access_token(user.id, user.email)
    refresh_token = generate_refresh_token()

    # Store refresh token
    user_agent, ip_address = get_client_info(request)
    await crud_token.create_refresh_token(
        db,
        user_id=user.id,
        token=refresh_token,
        expires_at=get_refresh_token_expiry(),
        user_agent=user_agent,
        ip_address=ip_address,
    )

    # Set refresh cookie
    set_refresh_cookie(response, refresh_token)

    return AuthResponse(
        user=UserOut.from_orm_with_prefix(user),
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
    )


# SIGN IN (Login)

@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login with email and password",
    description="Authenticate user and return access token. Refresh token is set as HttpOnly cookie.",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
    },
)
async def login(
    credentials: UserLogin,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user with email and password."""
    user = await crud_user.get_user_by_email(db, credentials.email)

    # Don't reveal whether email exists
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise AuthHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=AuthErrorCodes.INVALID_CREDENTIALS,
            message="Invalid email or password",
        )

    # Check if user has a password (not OAuth-only)
    if user.hashed_password is None:
        raise AuthHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=AuthErrorCodes.INVALID_CREDENTIALS,
            message="Invalid email or password",
        )

    # Generate tokens
    access_token, expires_in = create_access_token(user.id, user.email)
    refresh_token = generate_refresh_token()

    # Store refresh token
    user_agent, ip_address = get_client_info(request)
    await crud_token.create_refresh_token(
        db,
        user_id=user.id,
        token=refresh_token,
        expires_at=get_refresh_token_expiry(),
        user_agent=user_agent,
        ip_address=ip_address,
    )

    # Set refresh cookie
    set_refresh_cookie(response, refresh_token)

    return AuthResponse(
        user=UserOut.from_orm_with_prefix(user),
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
    )


# SWAGGER UI LOGIN (Form-based for OAuth2 compatibility)

@router.post(
    "/token",
    response_model=Token,
    include_in_schema=True,
    summary="OAuth2 compatible token endpoint",
    description="Used by Swagger UI for authentication. Use /login for regular auth.",
)
async def login_swagger(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """OAuth2 compatible login for Swagger UI."""
    user = await crud_user.get_user_by_email(db, username)
    if not user or not verify_password(password, user.hashed_password):
        raise AuthHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=AuthErrorCodes.INVALID_CREDENTIALS,
            message="Invalid credentials",
        )

    access_token, _ = create_access_token(user.id, user.email)
    refresh_token = generate_refresh_token()

    user_agent, ip_address = get_client_info(request)
    await crud_token.create_refresh_token(
        db,
        user_id=user.id,
        token=refresh_token,
        expires_at=get_refresh_token_expiry(),
        user_agent=user_agent,
        ip_address=ip_address,
    )

    set_refresh_cookie(response, refresh_token)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


# CURRENT USER (/me)

@router.get(
    "/me",
    response_model=MeResponse,
    summary="Get current user",
    description="Returns the currently authenticated user's information.",
    responses={
        200: {"description": "User information"},
        401: {"description": "Not authenticated"},
    },
)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user."""
    return MeResponse(user=UserOut.from_orm_with_prefix(current_user))



@router.post(
    "/refresh",
    response_model=RefreshResponse,
    summary="Refresh access token",
    description="Get a new access token using the refresh token from HttpOnly cookie.",
    responses={
        200: {"description": "New access token issued"},
        401: {"description": "Invalid or expired refresh token"},
    },
)
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Refresh the access token using the refresh token cookie."""
    # Get refresh token from cookie
    token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not token:
        raise AuthHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=AuthErrorCodes.REFRESH_EXPIRED_OR_INVALID,
            message="Refresh token not found",
        )

    # Validate refresh token
    token_entry = await crud_token.get_refresh_token_by_hash(db, token)
    if not token_entry:
        clear_refresh_cookie(response)
        raise AuthHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=AuthErrorCodes.REFRESH_EXPIRED_OR_INVALID,
            message="Invalid refresh token",
        )

    # Check expiration
    if token_entry.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        await crud_token.revoke_refresh_token(db, token)
        clear_refresh_cookie(response)
        raise AuthHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=AuthErrorCodes.REFRESH_EXPIRED_OR_INVALID,
            message="Refresh token expired",
        )

    # Get user
    user = token_entry.user
    if not user:
        clear_refresh_cookie(response)
        raise AuthHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=AuthErrorCodes.REFRESH_EXPIRED_OR_INVALID,
            message="User not found",
        )

    # Token rotation: revoke old token and issue new one
    await crud_token.revoke_refresh_token(db, token)
    new_refresh_token = generate_refresh_token()

    user_agent, ip_address = get_client_info(request)
    await crud_token.create_refresh_token(
        db,
        user_id=user.id,
        token=new_refresh_token,
        expires_at=get_refresh_token_expiry(),
        user_agent=user_agent,
        ip_address=ip_address,
    )

    # Set new refresh cookie
    set_refresh_cookie(response, new_refresh_token)

    # Generate new access token
    access_token, expires_in = create_access_token(user.id, user.email)

    return RefreshResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
    )



@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout",
    description="Revoke refresh token and clear cookie.",
)
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Logout user by revoking refresh token and clearing cookie."""
    token = request.cookies.get(REFRESH_COOKIE_NAME)
    if token:
        await crud_token.revoke_refresh_token(db, token)

    clear_refresh_cookie(response)
    return Response(status_code=status.HTTP_204_NO_CONTENT)



@router.post(
    "/password/forgot",
    response_model=StatusResponse,
    summary="Request password reset",
    description="Send password reset email. Always returns success for security.",
)
async def forgot_password(
    request_data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Request a password reset.

    Security: Always returns the same response regardless of whether
    the email exists to prevent email enumeration.
    """
    user = await crud_user.get_user_by_email(db, request_data.email)

    if user and user.hashed_password is not None:
        # Generate reset token
        reset_token = crud_token.generate_token()

        # Store token (hashed)
        await crud_token.create_password_reset_token(
            db,
            user_id=user.id,
            token=reset_token,
            expires_at=get_password_reset_expiry(),
        )

        # TODO: Send email with reset link
        # For now, log it (in production, integrate with email service)
        # reset_link = f"{settings.FRONTEND_URL}/auth/reset-password?token={reset_token}"
        # await email_service.send_password_reset(user.email, reset_link)

        # In development, you can see the token in logs
        if settings.is_development:
            import logging
            logging.info(f"Password reset token for {user.email}: {reset_token}")

    # Always return success
    return StatusResponse(status="ok")



@router.post(
    "/password/reset",
    response_model=StatusResponse,
    summary="Reset password with token",
    description="Reset password using the token from the email.",
    responses={
        200: {"description": "Password reset successful"},
        400: {"description": "Invalid or expired token"},
    },
)
async def reset_password(
    request_data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reset password using a valid reset token."""
    # Validate token
    token_entry = await crud_token.get_password_reset_token(db, request_data.token)

    if not token_entry:
        raise AuthHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=AuthErrorCodes.TOKEN_INVALID_OR_EXPIRED,
            message="Invalid or expired reset token",
        )

    # Get user
    user = await crud_user.get_user_by_id(db, token_entry.user_id)
    if not user:
        raise AuthHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=AuthErrorCodes.TOKEN_INVALID_OR_EXPIRED,
            message="Invalid or expired reset token",
        )

    # Update password
    await crud_user.update_user_password(db, user, request_data.new_password)

    # Mark token as used
    await crud_token.mark_password_reset_token_used(db, token_entry.id)

    # Revoke all refresh tokens for security
    await crud_token.revoke_all_user_tokens(db, user.id)

    return StatusResponse(status="ok")


# GOOGLE OAUTH - AUTHORIZE

@router.get(
    "/oauth/google/authorize",
    summary="Start Google OAuth flow",
    description="Redirects to Google for authentication.",
    responses={
        302: {"description": "Redirect to Google"},
        400: {"description": "OAuth not configured"},
    },
)
async def google_authorize(response: Response):
    """Initiate Google OAuth flow."""
    if not settings.google_oauth_enabled:
        raise AuthHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=AuthErrorCodes.OAUTH_NOT_CONFIGURED,
            message="Google OAuth is not configured",
        )

    # Generate CSRF state
    state = secrets.token_urlsafe(32)

    # Build Google OAuth URL
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }

    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

    # Set state in cookie for CSRF validation
    redirect_response = RedirectResponse(url=auth_url, status_code=status.HTTP_302_FOUND)
    redirect_response.set_cookie(
        key=OAUTH_STATE_COOKIE_NAME,
        value=state,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=600,  # 10 minutes
    )

    return redirect_response


# GOOGLE OAUTH - CALLBACK

@router.get(
    "/oauth/google/callback",
    summary="Google OAuth callback",
    description="Handles the callback from Google after authentication.",
    responses={
        302: {"description": "Redirect to frontend"},
        400: {"description": "OAuth error"},
    },
)
async def google_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Handle Google OAuth callback."""
    frontend_callback = settings.FRONTEND_AUTH_CALLBACK_URL

    # Check for OAuth error
    if error:
        return RedirectResponse(
            url=f"{frontend_callback}?error=oauth_denied",
            status_code=status.HTTP_302_FOUND,
        )

    if not code or not state:
        return RedirectResponse(
            url=f"{frontend_callback}?error=invalid_request",
            status_code=status.HTTP_302_FOUND,
        )

    # Validate CSRF state
    stored_state = request.cookies.get(OAUTH_STATE_COOKIE_NAME)
    if not stored_state or stored_state != state:
        return RedirectResponse(
            url=f"{frontend_callback}?error=state_mismatch",
            status_code=status.HTTP_302_FOUND,
        )

    try:
        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                },
            )

            if token_response.status_code != 200:
                return RedirectResponse(
                    url=f"{frontend_callback}?error=token_exchange_failed",
                    status_code=status.HTTP_302_FOUND,
                )

            tokens = token_response.json()
            google_access_token = tokens.get("access_token")

            # Get user info from Google
            userinfo_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {google_access_token}"},
            )

            if userinfo_response.status_code != 200:
                return RedirectResponse(
                    url=f"{frontend_callback}?error=userinfo_failed",
                    status_code=status.HTTP_302_FOUND,
                )

            userinfo = userinfo_response.json()

    except Exception:
        return RedirectResponse(
            url=f"{frontend_callback}?error=oauth_error",
            status_code=status.HTTP_302_FOUND,
        )

    # Extract user info
    email = userinfo.get("email")
    full_name = userinfo.get("name")
    email_verified = userinfo.get("verified_email", False)

    if not email:
        return RedirectResponse(
            url=f"{frontend_callback}?error=no_email",
            status_code=status.HTTP_302_FOUND,
        )

    # Find or create user
    user = await crud_user.get_user_by_email(db, email)

    if not user:
        # Create new OAuth user
        user = await crud_user.create_oauth_user(
            db,
            email=email,
            full_name=full_name,
            auth_provider="google",
            email_verified=email_verified,
        )
    elif user.auth_provider == "password" and user.hashed_password:
        # User exists with password - link Google account
        # Update email_verified if Google says it's verified
        if email_verified and not user.email_verified:
            await crud_user.update_user_email_verified(db, user, True)

    # Generate tokens
    access_token, expires_in = create_access_token(user.id, user.email)
    refresh_token = generate_refresh_token()

    # Store refresh token
    user_agent = request.headers.get("user-agent")
    forwarded_for = request.headers.get("x-forwarded-for")
    ip_address = forwarded_for.split(",")[0].strip() if forwarded_for else (
        request.client.host if request.client else None
    )

    await crud_token.create_refresh_token(
        db,
        user_id=user.id,
        token=refresh_token,
        expires_at=get_refresh_token_expiry(),
        user_agent=user_agent,
        ip_address=ip_address,
    )

    # Build redirect URL with access token
    # Note: Access token in URL fragment is not ideal but common for OAuth
    # The frontend should extract it and store securely
    redirect_url = f"{frontend_callback}?success=1&access_token={access_token}&expires_in={expires_in}"

    redirect_response = RedirectResponse(
        url=redirect_url,
        status_code=status.HTTP_302_FOUND,
    )

    # Set refresh cookie
    set_refresh_cookie(redirect_response, refresh_token)

    # Clear OAuth state cookie
    redirect_response.delete_cookie(key=OAUTH_STATE_COOKIE_NAME)

    return redirect_response

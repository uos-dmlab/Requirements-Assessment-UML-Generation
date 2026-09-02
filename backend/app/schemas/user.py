from typing import Optional
from pydantic import BaseModel, EmailStr, Field, model_validator



class UserBase(BaseModel):
    """Base user fields."""
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration."""
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6)
    password_confirm: str = Field(..., min_length=6)

    @model_validator(mode="after")
    def passwords_match(self) -> "UserCreate":
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self


class UserLogin(UserBase):
    """Schema for user login."""
    password: str


class UserOut(BaseModel):
    """Schema for user output in responses."""
    id: str  # Return as string for frontend compatibility
    full_name: Optional[str] = None
    email: EmailStr
    email_verified: bool = False

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_prefix(cls, user) -> "UserOut":
        """Create UserOut from ORM model with prefixed ID."""
        return cls(
            id=f"usr_{user.id}",
            full_name=user.full_name,
            email=user.email,
            email_verified=user.email_verified
        )



class AuthResponse(BaseModel):
    """Response for login/register with tokens."""
    user: UserOut
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshResponse(BaseModel):
    """Response for token refresh."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class MeResponse(BaseModel):
    """Response for /me endpoint."""
    user: UserOut


class StatusResponse(BaseModel):
    """Generic status response."""
    status: str = "ok"



class ForgotPasswordRequest(BaseModel):
    """Request for forgot password."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Request for password reset."""
    token: str
    new_password: str = Field(..., min_length=6)
    new_password_confirm: str = Field(..., min_length=6)

    @model_validator(mode="after")
    def passwords_match(self) -> "ResetPasswordRequest":
        if self.new_password != self.new_password_confirm:
            raise ValueError("Passwords do not match")
        return self



class Token(BaseModel):
    """Legacy token response - kept for Swagger UI compatibility."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

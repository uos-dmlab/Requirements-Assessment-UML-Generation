"""Pydantic schemas for Account Settings API."""

from pydantic import BaseModel, Field, model_validator


class ChangePasswordRequest(BaseModel):
    """Request body for changing password."""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6)
    new_password_confirm: str = Field(..., min_length=6)

    @model_validator(mode="after")
    def passwords_match(self) -> "ChangePasswordRequest":
        if self.new_password != self.new_password_confirm:
            raise ValueError("New passwords do not match")
        return self


class DeleteAccountRequest(BaseModel):
    """Request body for deleting account."""
    password: str = Field(..., min_length=1)
    confirm_text: str = Field(..., min_length=1)

    @model_validator(mode="after")
    def validate_confirm_text(self) -> "DeleteAccountRequest":
        if self.confirm_text != "DELETE":
            raise ValueError("Confirmation text must be 'DELETE'")
        return self


class AccountStatusResponse(BaseModel):
    """Response for account operations."""
    status: str

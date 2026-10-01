"""Authentication and authorization Pydantic schemas."""

from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class LoginRequest(BaseModel):
    """Credentials required for user login."""

    email: EmailStr = Field(..., description="Registered user email address")
    password: str = Field(..., min_length=1, description="Account password")


class TokenResponse(BaseModel):
    """JWT bearer token pair response."""

    access_token: str = Field(..., description="Encoded JWT access token")
    refresh_token: str = Field(..., description="Encoded JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type designation")


class RefreshTokenRequest(BaseModel):
    """Payload for refreshing an expired access token."""

    refresh_token: str = Field(..., min_length=1, description="Active JWT refresh token")


class RegisterRequest(BaseModel):
    """Payload for registering a new user."""

    model_config = ConfigDict(populate_by_name=True)

    email: EmailStr = Field(..., description="Valid email address for the new account")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password with at least 8 characters",
    )
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Full legal name of the user",
    )
    phone: str | None = Field(
        default=None,
        max_length=20,
        validation_alias=AliasChoices("phone", "phone_number"),
        description="Contact telephone number",
    )
    role: UserRole = Field(
        default=UserRole.CITIZEN,
        description="User system role (defaults to CITIZEN)",
    )

    @property
    def phone_number(self) -> str | None:
        """Alias property for compatibility with services expecting phone_number."""
        return self.phone

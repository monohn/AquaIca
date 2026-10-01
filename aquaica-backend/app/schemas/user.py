"""User-related Pydantic schemas for AquaIca."""

from __future__ import annotations

from datetime import datetime
from typing import Any
import uuid

from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.models.user import UserRole


class UserResponse(BaseModel):
    """User response representation."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID = Field(..., description="Unique user identifier")
    email: EmailStr = Field(..., description="Registered user email")
    full_name: str = Field(..., description="Full legal name of the user")
    phone: str | None = Field(
        default=None,
        validation_alias=AliasChoices("phone", "phone_number"),
        description="Contact telephone number",
    )
    role: UserRole = Field(..., description="System role assigned to user")
    is_active: bool = Field(default=True, description="Account active status")
    created_at: datetime = Field(..., description="Timestamp of user account creation")
    updated_at: datetime | None = Field(
        default=None,
        description="Timestamp of last account update",
    )


class UserUpdate(BaseModel):
    """Payload for modifying an existing user profile."""

    model_config = ConfigDict(populate_by_name=True)

    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
        description="Updated full name",
    )
    phone: str | None = Field(
        default=None,
        max_length=20,
        validation_alias=AliasChoices("phone", "phone_number"),
        description="Updated contact telephone number",
    )


class UserListResponse(BaseModel):
    """Paginated list response containing user accounts."""

    model_config = ConfigDict(from_attributes=True)

    items: list[UserResponse] = Field(
        default_factory=list,
        description="List of user records",
    )
    total: int = Field(..., ge=0, description="Total matching users in database")
    page: int = Field(default=1, ge=1, description="Current page number")
    size: int = Field(default=20, ge=1, description="Page size limit")

    @model_validator(mode="before")
    @classmethod
    def convert_tuple_or_mapping(cls, data: Any) -> Any:
        """Coerce tuple pair (items, total) from repository/service calls into schema dictionary."""
        if isinstance(data, (tuple, list)) and len(data) == 2:
            items, total = data
            return {
                "items": items,
                "total": total,
                "page": 1,
                "size": len(items) if hasattr(items, "__len__") else 20,
            }
        return data

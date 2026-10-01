"""Incident reporting and lifecycle management Pydantic schemas."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
import uuid

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.models.incident import IncidentCategory, IncidentPriority, IncidentStatus
from app.schemas.user import UserResponse


class IncidentCreate(BaseModel):
    """Schema for creating a new citizen incident report."""

    title: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Short summary of the incident",
    )
    description: str = Field(
        ...,
        min_length=5,
        description="Detailed description of the issue",
    )
    category: IncidentCategory = Field(
        ...,
        description="Category of the water/sanitation incident",
    )
    priority: IncidentPriority | None = Field(
        default=IncidentPriority.LOW,
        description="Initial priority level assigned to the incident",
    )
    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="GPS latitude coordinate between -90 and 90",
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="GPS longitude coordinate between -180 and 180",
    )
    address: str | None = Field(
        default=None,
        max_length=500,
        description="Street address or reference point",
    )
    district: str | None = Field(
        default=None,
        max_length=100,
        description="District within the province of Ica",
    )


class IncidentUpdate(BaseModel):
    """Schema for updating incident details."""

    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=200,
        description="Updated incident title",
    )
    description: str | None = Field(
        default=None,
        min_length=5,
        description="Updated incident description",
    )
    category: IncidentCategory | None = Field(
        default=None,
        description="Updated incident category",
    )
    priority: IncidentPriority | None = Field(
        default=None,
        description="Updated priority level",
    )
    address: str | None = Field(
        default=None,
        max_length=500,
        description="Updated street address or reference",
    )
    district: str | None = Field(
        default=None,
        max_length=100,
        description="Updated district name",
    )


class IncidentStatusUpdate(BaseModel):
    """Schema for administrative transition of incident status."""

    model_config = ConfigDict(populate_by_name=True)

    status: IncidentStatus = Field(
        ...,
        description="Target lifecycle status for the incident",
    )
    comment: str | None = Field(
        default=None,
        validation_alias=AliasChoices("comment", "notes"),
        description="Administrative comment or rationale for the status change",
    )

    @property
    def notes(self) -> str | None:
        """Alias property matching service usage."""
        return self.comment


class IncidentSummaryResponse(BaseModel):
    """Compact summary of an incident for nested relationship representations."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Unique incident identifier")
    code: str = Field(..., description="Formatted tracking code (e.g. INC-000001)")
    title: str = Field(..., description="Incident title")
    category: IncidentCategory = Field(..., description="Incident category")
    priority: IncidentPriority = Field(..., description="Urgency priority level")
    status: IncidentStatus = Field(..., description="Lifecycle status")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude coordinate")
    address: str | None = Field(default=None, description="Street address or reference")
    district: str | None = Field(default=None, description="District within Ica")
    created_at: datetime = Field(..., description="Incident creation timestamp")


class IncidentResponse(BaseModel):
    """Full representation of an incident including reporter profile."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Unique incident identifier")
    code: str = Field(..., description="Formatted tracking code (e.g. INC-000001)")
    title: str = Field(..., description="Incident title")
    description: str = Field(..., description="Detailed description")
    category: IncidentCategory = Field(..., description="Incident category")
    priority: IncidentPriority = Field(..., description="Urgency priority level")
    status: IncidentStatus = Field(..., description="Lifecycle status")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude coordinate")
    address: str | None = Field(default=None, description="Street address or reference")
    district: str | None = Field(default=None, description="District within Ica")
    reporter_id: uuid.UUID = Field(..., description="UUID of user who reported this incident")
    reporter: UserResponse | None = Field(
        default=None,
        description="Nested profile of reporting user",
    )
    created_at: datetime = Field(..., description="Incident report creation timestamp")
    updated_at: datetime = Field(..., description="Incident report last update timestamp")


class IncidentListResponse(BaseModel):
    """Paginated list of incidents."""

    model_config = ConfigDict(from_attributes=True)

    items: list[IncidentResponse] = Field(
        default_factory=list,
        description="List of incident records",
    )
    total: int = Field(..., ge=0, description="Total matching incidents count")
    page: int = Field(default=1, ge=1, description="Current page number")
    size: int = Field(default=20, ge=1, description="Number of items per page")

    @model_validator(mode="before")
    @classmethod
    def convert_tuple_or_mapping(cls, data: Any) -> Any:
        """Coerce tuple pair (items, total) from service calls into schema dictionary."""
        if isinstance(data, (tuple, list)) and len(data) == 2:
            items, total = data
            return {
                "items": items,
                "total": total,
                "page": 1,
                "size": len(items) if hasattr(items, "__len__") else 20,
            }
        return data


class IncidentFilters(BaseModel):
    """Filter criteria for querying incidents."""

    status: IncidentStatus | None = Field(default=None, description="Filter by status")
    category: IncidentCategory | None = Field(default=None, description="Filter by category")
    priority: IncidentPriority | None = Field(default=None, description="Filter by priority")
    district: str | None = Field(default=None, description="Filter by district")
    reporter_id: uuid.UUID | None = Field(default=None, description="Filter by reporter UUID")
    date_from: datetime | date | None = Field(default=None, description="Filter from date/datetime")
    date_to: datetime | date | None = Field(default=None, description="Filter to date/datetime")

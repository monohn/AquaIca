"""Work assignment Pydantic schemas for AquaIca."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
import uuid

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.assignment import AssignmentStatus
from app.schemas.incident import IncidentSummaryResponse
from app.schemas.user import UserResponse


class AssignmentCreate(BaseModel):
    """Payload for assigning an incident to a field technician."""

    incident_id: uuid.UUID = Field(
        ...,
        description="Unique identifier of the incident to assign",
    )
    technician_id: uuid.UUID = Field(
        ...,
        description="Unique identifier of the assigned technician",
    )
    notes: str | None = Field(
        default=None,
        description="Instructions or notes for the technician",
    )
    scheduled_date: date | None = Field(
        default=None,
        description="Scheduled target date for inspection or repair",
    )


class AssignmentUpdate(BaseModel):
    """Payload for updating assignment notes or schedule."""

    notes: str | None = Field(
        default=None,
        description="Updated technician notes or instructions",
    )
    scheduled_date: date | None = Field(
        default=None,
        description="Updated scheduled execution date",
    )


class AssignmentStatusUpdate(BaseModel):
    """Payload for updating assignment execution status."""

    status: AssignmentStatus = Field(
        ...,
        description="New lifecycle status for the assignment",
    )
    notes: str | None = Field(
        default=None,
        description="Status transition work notes or completion details",
    )


class AssignmentResponse(BaseModel):
    """Detailed assignment representation including nested related entities."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Unique assignment identifier")
    incident_id: uuid.UUID = Field(..., description="Associated incident UUID")
    technician_id: uuid.UUID = Field(..., description="Assigned technician UUID")
    assigned_by_id: uuid.UUID = Field(..., description="Admin user UUID who created assignment")
    status: AssignmentStatus = Field(..., description="Current assignment lifecycle status")
    notes: str | None = Field(default=None, description="Assignment notes or instructions")
    scheduled_date: date | None = Field(default=None, description="Scheduled work date")
    completed_at: datetime | None = Field(default=None, description="Completion timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    # Nested relationships
    incident: IncidentSummaryResponse | None = Field(
        default=None,
        description="Nested incident summary information",
    )
    technician: UserResponse | None = Field(
        default=None,
        description="Nested technician profile information",
    )
    assigned_by: UserResponse | None = Field(
        default=None,
        description="Nested assigner user profile information",
    )


class AssignmentListResponse(BaseModel):
    """Paginated list of assignments."""

    model_config = ConfigDict(from_attributes=True)

    items: list[AssignmentResponse] = Field(
        default_factory=list,
        description="List of assignment records",
    )
    total: int = Field(..., ge=0, description="Total matching assignments count")
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

"""Evidence and diagnostic media Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
import uuid

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.evidence import EvidenceType
from app.schemas.user import UserResponse


class EvidenceCreate(BaseModel):
    """Metadata schema for uploading evidence attachments."""

    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional description of the evidence file",
    )
    evidence_type: EvidenceType = Field(
        default=EvidenceType.REPORT,
        description="Classification type of the evidence",
    )
    incident_id: uuid.UUID | None = Field(
        default=None,
        description="Associated incident UUID if applicable",
    )
    assignment_id: uuid.UUID | None = Field(
        default=None,
        description="Associated assignment UUID if applicable",
    )


class EvidenceResponse(BaseModel):
    """Complete evidence file response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Unique evidence record identifier")
    incident_id: uuid.UUID | None = Field(
        default=None,
        description="Associated incident UUID",
    )
    assignment_id: uuid.UUID | None = Field(
        default=None,
        description="Associated assignment UUID",
    )
    uploaded_by_id: uuid.UUID = Field(
        ...,
        description="UUID of user who uploaded file",
    )
    file_path: str = Field(
        ...,
        description="File path or URL for retrieving file content",
    )
    file_name: str = Field(..., description="Original upload filename")
    file_type: str = Field(..., description="File MIME type")
    description: str | None = Field(
        default=None,
        description="Text description of the evidence file",
    )
    evidence_type: EvidenceType = Field(
        ...,
        description="Classification category of the evidence",
    )
    created_at: datetime = Field(..., description="Upload timestamp")
    uploaded_by: UserResponse | None = Field(
        default=None,
        description="User profile of uploader",
    )


class EvidenceListResponse(BaseModel):
    """List response containing evidence records."""

    model_config = ConfigDict(from_attributes=True)

    items: list[EvidenceResponse] = Field(
        default_factory=list,
        description="List of evidence items",
    )
    total: int = Field(default=0, ge=0, description="Total evidence items count")

    @model_validator(mode="before")
    @classmethod
    def convert_from_list_or_tuple(cls, data: Any) -> Any:
        """Coerce raw list or tuple pair from service layer into schema dictionary."""
        if isinstance(data, list):
            return {"items": data, "total": len(data)}
        if isinstance(data, (tuple, list)) and len(data) == 2:
            items, total = data
            return {"items": items, "total": total}
        return data

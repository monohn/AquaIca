"""SQLAlchemy model for Evidence."""

from datetime import datetime
import enum
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.assignment import Assignment
    from app.models.incident import Incident
    from app.models.user import User


class EvidenceType(str, enum.Enum):
    """Classification for uploaded evidence files."""

    REPORT = "REPORT"
    DIAGNOSIS = "DIAGNOSIS"
    REPAIR = "REPAIR"
    VERIFICATION = "VERIFICATION"


class Evidence(Base):
    """Evidence database model storing photos, documents, and diagnostics."""

    __tablename__ = "evidence"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    incident_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    assignment_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("assignments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    uploaded_by_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    file_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    evidence_type: Mapped[EvidenceType] = mapped_column(
        Enum(EvidenceType, name="evidence_type"),
        nullable=False,
        default=EvidenceType.REPORT,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    incident: Mapped["Incident | None"] = relationship(
        "Incident",
        back_populates="evidence",
        foreign_keys=[incident_id],
    )
    assignment: Mapped["Assignment | None"] = relationship(
        "Assignment",
        back_populates="evidence",
        foreign_keys=[assignment_id],
    )
    uploaded_by: Mapped["User"] = relationship(
        "User",
        back_populates="uploaded_evidence",
        foreign_keys=[uploaded_by_id],
    )

"""SQLAlchemy model for Incidents."""

from datetime import datetime
import enum
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
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
    from app.models.evidence import Evidence
    from app.models.incident_history import IncidentHistory
    from app.models.user import User


class IncidentCategory(str, enum.Enum):
    """Categories of water and sanitation incidents."""

    FUGA = "FUGA"
    ROTURA_TUBERIA = "ROTURA_TUBERIA"
    ANIEGO = "ANIEGO"
    BAJA_PRESION = "BAJA_PRESION"
    AGUA_TURBIA = "AGUA_TURBIA"
    CORTE_SERVICIO = "CORTE_SERVICIO"
    OTRO = "OTRO"


class IncidentPriority(str, enum.Enum):
    """Urgency/priority level of reported incidents."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentStatus(str, enum.Enum):
    """Lifecycle status of an incident report."""

    REPORTED = "REPORTED"
    VALIDATED = "VALIDATED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    REJECTED = "REJECTED"


class Incident(Base):
    """Incident database model for water service issues in Ica."""

    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    category: Mapped[IncidentCategory] = mapped_column(
        Enum(IncidentCategory, name="incident_category"),
        nullable=False,
    )
    priority: Mapped[IncidentPriority] = mapped_column(
        Enum(IncidentPriority, name="incident_priority"),
        nullable=False,
        default=IncidentPriority.MEDIUM,
    )
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus, name="incident_status"),
        nullable=False,
        default=IncidentStatus.REPORTED,
    )
    latitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    longitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    district: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    reporter_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    reporter: Mapped["User"] = relationship(
        "User",
        back_populates="reported_incidents",
        foreign_keys=[reporter_id],
    )
    assignments: Mapped[list["Assignment"]] = relationship(
        "Assignment",
        back_populates="incident",
        cascade="all, delete-orphan",
    )
    evidence: Mapped[list["Evidence"]] = relationship(
        "Evidence",
        back_populates="incident",
        cascade="all, delete-orphan",
    )
    history: Mapped[list["IncidentHistory"]] = relationship(
        "IncidentHistory",
        back_populates="incident",
        cascade="all, delete-orphan",
        order_by="IncidentHistory.created_at.desc()",
    )

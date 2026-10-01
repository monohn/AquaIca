"""SQLAlchemy model for Users."""

from datetime import datetime
import enum
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import Boolean, DateTime, Enum, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.assignment import Assignment
    from app.models.evidence import Evidence
    from app.models.incident import Incident
    from app.models.incident_history import IncidentHistory


class UserRole(str, enum.Enum):
    """Enumeration of system user roles."""

    CITIZEN = "CITIZEN"
    ADMIN = "ADMIN"
    TECHNICIAN = "TECHNICIAN"


class User(Base):
    """User database model representing citizens, admins, and technicians."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        nullable=False,
        default=UserRole.CITIZEN,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
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
    reported_incidents: Mapped[list["Incident"]] = relationship(
        "Incident",
        back_populates="reporter",
        foreign_keys="Incident.reporter_id",
    )
    assigned_tasks: Mapped[list["Assignment"]] = relationship(
        "Assignment",
        back_populates="technician",
        foreign_keys="Assignment.technician_id",
    )
    created_assignments: Mapped[list["Assignment"]] = relationship(
        "Assignment",
        back_populates="assigned_by",
        foreign_keys="Assignment.assigned_by_id",
    )
    uploaded_evidence: Mapped[list["Evidence"]] = relationship(
        "Evidence",
        back_populates="uploaded_by",
        foreign_keys="Evidence.uploaded_by_id",
    )
    history_changes: Mapped[list["IncidentHistory"]] = relationship(
        "IncidentHistory",
        back_populates="changed_by",
        foreign_keys="IncidentHistory.changed_by_id",
    )

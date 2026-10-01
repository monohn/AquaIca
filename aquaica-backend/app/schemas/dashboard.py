"""Administrative dashboard and analytics Pydantic schemas."""

from __future__ import annotations

from typing import Any
import uuid

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.incident import IncidentCategory, IncidentPriority
from app.schemas.incident import IncidentResponse
from app.schemas.user import UserResponse


class DashboardStats(BaseModel):
    """Aggregate counts of incidents by operational lifecycle status."""

    total_incidents: int = Field(
        default=0,
        ge=0,
        description="Total number of reported incidents",
    )
    pending: int = Field(
        default=0,
        ge=0,
        description="Count of pending or reported incidents",
    )
    in_progress: int = Field(
        default=0,
        ge=0,
        description="Count of incidents actively being addressed",
    )
    resolved: int = Field(
        default=0,
        ge=0,
        description="Count of resolved incidents",
    )
    closed: int = Field(
        default=0,
        ge=0,
        description="Count of formally closed incidents",
    )
    rejected: int = Field(
        default=0,
        ge=0,
        description="Count of rejected incident reports",
    )


class IncidentStats(BaseModel):
    """Aggregated incident breakdown used across backend analytics."""

    total: int = Field(default=0, ge=0, description="Total incident count")
    by_status: dict[str, int] = Field(
        default_factory=dict,
        description="Counts grouped by status",
    )
    by_category: dict[str, int] = Field(
        default_factory=dict,
        description="Counts grouped by category",
    )
    by_district: dict[str, int] = Field(
        default_factory=dict,
        description="Counts grouped by district",
    )
    by_priority: dict[str, int] = Field(
        default_factory=dict,
        description="Counts grouped by priority",
    )


class IncidentsByCategory(BaseModel):
    """Aggregated count of incidents in a specific category."""

    category: IncidentCategory | str = Field(
        ...,
        description="Incident category enum or string designation",
    )
    count: int = Field(
        ...,
        ge=0,
        description="Number of incidents in this category",
    )


class IncidentsByDistrict(BaseModel):
    """Aggregated count of incidents in a specific district."""

    district: str = Field(..., description="District name within Ica province")
    count: int = Field(
        ...,
        ge=0,
        description="Number of incidents in this district",
    )


class IncidentsByPriority(BaseModel):
    """Aggregated count of incidents by priority level."""

    priority: IncidentPriority | str = Field(
        ...,
        description="Incident priority enum or string designation",
    )
    count: int = Field(
        ...,
        ge=0,
        description="Number of incidents with this priority",
    )


class HeatmapPoint(BaseModel):
    """Geographic point coordinate and density weight for map heatmaps."""

    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="GPS latitude coordinate",
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="GPS longitude coordinate",
    )
    weight: float = Field(
        default=1.0,
        ge=0.0,
        description="Density weight or incident count at coordinate",
    )


class TechnicianWorkload(BaseModel):
    """Operational workload summary for a field technician."""

    model_config = ConfigDict(from_attributes=True)

    technician: UserResponse | None = Field(
        default=None,
        description="Full profile of the technician",
    )
    technician_id: uuid.UUID | None = Field(
        default=None,
        description="Technician unique identifier",
    )
    technician_name: str | None = Field(
        default=None,
        description="Full name of technician",
    )
    active_assignments: int = Field(
        default=0,
        ge=0,
        description="Count of currently active assignments",
    )
    completed_assignments: int = Field(
        default=0,
        ge=0,
        description="Count of completed assignments",
    )


class DashboardResponse(BaseModel):
    """Consolidated metrics and recent activities for the admin dashboard."""

    model_config = ConfigDict(from_attributes=True)

    stats: DashboardStats | IncidentStats | dict[str, Any] = Field(
        ...,
        description="Core incident statistics breakdown",
    )
    by_category: list[IncidentsByCategory] = Field(
        default_factory=list,
        description="Aggregated count by category",
    )
    by_district: list[IncidentsByDistrict] = Field(
        default_factory=list,
        description="Aggregated count by district",
    )
    by_priority: list[IncidentsByPriority] = Field(
        default_factory=list,
        description="Aggregated count by priority",
    )
    recent_incidents: list[IncidentResponse] = Field(
        default_factory=list,
        description="List of recently submitted incident reports",
    )

    @model_validator(mode="before")
    @classmethod
    def populate_breakdowns_from_stats(cls, data: Any) -> Any:
        """Derive category, district, and priority lists from stats dictionary if not provided."""
        if isinstance(data, dict):
            stats_val = data.get("stats")
            if hasattr(stats_val, "by_category") and not data.get("by_category"):
                data["by_category"] = [
                    {"category": k, "count": v}
                    for k, v in getattr(stats_val, "by_category", {}).items()
                ]
            elif (
                isinstance(stats_val, dict)
                and "by_category" in stats_val
                and not data.get("by_category")
            ):
                data["by_category"] = [
                    {"category": k, "count": v}
                    for k, v in stats_val["by_category"].items()
                ]

            if hasattr(stats_val, "by_district") and not data.get("by_district"):
                data["by_district"] = [
                    {"district": k, "count": v}
                    for k, v in getattr(stats_val, "by_district", {}).items()
                ]
            elif (
                isinstance(stats_val, dict)
                and "by_district" in stats_val
                and not data.get("by_district")
            ):
                data["by_district"] = [
                    {"district": k, "count": v}
                    for k, v in stats_val["by_district"].items()
                ]

            if hasattr(stats_val, "by_priority") and not data.get("by_priority"):
                data["by_priority"] = [
                    {"priority": k, "count": v}
                    for k, v in getattr(stats_val, "by_priority", {}).items()
                ]
            elif (
                isinstance(stats_val, dict)
                and "by_priority" in stats_val
                and not data.get("by_priority")
            ):
                data["by_priority"] = [
                    {"priority": k, "count": v}
                    for k, v in stats_val["by_priority"].items()
                ]

        return data

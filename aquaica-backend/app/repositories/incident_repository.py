from datetime import datetime, date
from uuid import UUID
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.incident import Incident, IncidentStatus, IncidentCategory, IncidentPriority
from app.repositories.base import BaseRepository

class IncidentRepository(BaseRepository[Incident]):
    """Incident repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(Incident, db)

    def _build_filter_query(self, status: IncidentStatus | None = None, category: IncidentCategory | None = None, priority: IncidentPriority | None = None, district: str | None = None, reporter_id: UUID | None = None, date_from: datetime | None = None, date_to: datetime | None = None):
        query = select(Incident).options(selectinload(Incident.reporter))
        filters = []
        if status:
            filters.append(Incident.status == status)
        if category:
            filters.append(Incident.category == category)
        if priority:
            filters.append(Incident.priority == priority)
        if district:
            filters.append(Incident.district == district)
        if reporter_id:
            filters.append(Incident.reporter_id == reporter_id)
        if date_from:
            filters.append(Incident.created_at >= date_from)
        if date_to:
            filters.append(Incident.created_at <= date_to)
        if filters:
            query = query.where(and_(*filters))
        return query

    async def get_with_filters(self, status: IncidentStatus | None = None, category: IncidentCategory | None = None, priority: IncidentPriority | None = None, district: str | None = None, reporter_id: UUID | None = None, date_from: datetime | None = None, date_to: datetime | None = None, skip: int = 0, limit: int = 100) -> list[Incident]:
        """Get incidents with filters."""
        query = self._build_filter_query(status, category, priority, district, reporter_id, date_from, date_to)
        query = query.order_by(desc(Incident.created_at)).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_with_filters(self, status: IncidentStatus | None = None, category: IncidentCategory | None = None, priority: IncidentPriority | None = None, district: str | None = None, reporter_id: UUID | None = None, date_from: datetime | None = None, date_to: datetime | None = None) -> int:
        """Count incidents with filters."""
        query = self._build_filter_query(status, category, priority, district, reporter_id, date_from, date_to)
        count_query = select(func.count()).select_from(query.subquery())
        result = await self.db.execute(count_query)
        return result.scalar() or 0

    async def get_by_reporter(self, reporter_id: UUID, skip: int = 0, limit: int = 100) -> list[Incident]:
        """Get incidents by reporter."""
        result = await self.db.execute(
            select(Incident)
            .where(Incident.reporter_id == reporter_id)
            .order_by(desc(Incident.created_at))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_next_code(self) -> str:
        """Generate the next incident code INC-YYYY-NNNN."""
        current_year = date.today().year
        start_of_year = datetime(current_year, 1, 1)
        end_of_year = datetime(current_year, 12, 31, 23, 59, 59)
        
        result = await self.db.execute(
            select(func.count())
            .select_from(Incident)
            .where(and_(Incident.created_at >= start_of_year, Incident.created_at <= end_of_year))
        )
        count = result.scalar() or 0
        return f"INC-{current_year}-{count + 1:04d}"

    async def get_stats(self) -> dict[str, int]:
        """Get stats by status."""
        result = await self.db.execute(
            select(Incident.status, func.count(Incident.id)).group_by(Incident.status)
        )
        return {status.value if hasattr(status, 'value') else status: count for status, count in result.all()}

    async def get_by_category_stats(self) -> list[tuple[str, int]]:
        """Get stats by category."""
        result = await self.db.execute(
            select(Incident.category, func.count(Incident.id)).group_by(Incident.category)
        )
        return [(cat.value if hasattr(cat, 'value') else cat, count) for cat, count in result.all()]

    async def get_by_district_stats(self) -> list[tuple[str, int]]:
        """Get stats by district."""
        result = await self.db.execute(
            select(Incident.district, func.count(Incident.id)).group_by(Incident.district)
        )
        return [(dist, count) for dist, count in result.all() if dist]

    async def get_by_priority_stats(self) -> list[tuple[str, int]]:
        """Get stats by priority."""
        result = await self.db.execute(
            select(Incident.priority, func.count(Incident.id)).group_by(Incident.priority)
        )
        return [(prio.value if hasattr(prio, 'value') else prio, count) for prio, count in result.all()]

    async def get_heatmap_data(self) -> list[tuple[float, float, int]]:
        """Get heatmap data rounded to 3 decimals."""
        result = await self.db.execute(
            select(
                func.round(Incident.latitude, 3).label('lat'),
                func.round(Incident.longitude, 3).label('lng'),
                func.count(Incident.id)
            )
            .where(and_(Incident.latitude.isnot(None), Incident.longitude.isnot(None)))
            .group_by('lat', 'lng')
        )
        return [(float(row.lat), float(row.lng), row.count) for row in result.all()]

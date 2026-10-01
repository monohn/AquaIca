from uuid import UUID
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.assignment import Assignment, AssignmentStatus
from app.repositories.base import BaseRepository

class AssignmentRepository(BaseRepository[Assignment]):
    """Assignment repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(Assignment, db)

    async def get_by_incident(self, incident_id: UUID) -> list[Assignment]:
        """Get assignments for an incident."""
        result = await self.db.execute(
            select(Assignment)
            .options(selectinload(Assignment.technician))
            .where(Assignment.incident_id == incident_id)
        )
        return list(result.scalars().all())

    async def get_by_technician(self, technician_id: UUID, status_filter: AssignmentStatus | None = None, skip: int = 0, limit: int = 100) -> list[Assignment]:
        """Get assignments by technician with optional status filter."""
        query = select(Assignment).where(Assignment.technician_id == technician_id)
        if status_filter:
            query = query.where(Assignment.status == status_filter)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_technician(self, technician_id: UUID, status: AssignmentStatus | None = None) -> int:
        """Count assignments by technician."""
        query = select(func.count()).select_from(Assignment).where(Assignment.technician_id == technician_id)
        if status:
            query = query.where(Assignment.status == status)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_active_by_technician(self, technician_id: UUID) -> list[Assignment]:
        """Get active assignments for a technician."""
        active_statuses = [AssignmentStatus.PENDING, AssignmentStatus.ACCEPTED, AssignmentStatus.IN_PROGRESS]
        result = await self.db.execute(
            select(Assignment).where(
                and_(
                    Assignment.technician_id == technician_id,
                    Assignment.status.in_(active_statuses)
                )
            )
        )
        return list(result.scalars().all())

from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.evidence import Evidence
from app.repositories.base import BaseRepository

class EvidenceRepository(BaseRepository[Evidence]):
    """Evidence repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(Evidence, db)

    async def get_by_incident(self, incident_id: UUID) -> list[Evidence]:
        """Get evidence by incident."""
        result = await self.db.execute(
            select(Evidence).where(Evidence.incident_id == incident_id)
        )
        return list(result.scalars().all())

    async def get_by_assignment(self, assignment_id: UUID) -> list[Evidence]:
        """Get evidence by assignment."""
        result = await self.db.execute(
            select(Evidence).where(Evidence.assignment_id == assignment_id)
        )
        return list(result.scalars().all())

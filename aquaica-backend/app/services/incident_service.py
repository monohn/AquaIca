from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.repositories.incident_repository import IncidentRepository
from app.models.incident import Incident, IncidentStatus, IncidentCategory, IncidentPriority
from app.models.incident_history import IncidentHistory
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentStatusUpdate
from app.utils.exceptions import NotFoundException, BadRequestException, ForbiddenException

VALID_TRANSITIONS = {
    IncidentStatus.REPORTED: [IncidentStatus.VALIDATED, IncidentStatus.REJECTED],
    IncidentStatus.VALIDATED: [IncidentStatus.ASSIGNED],
    IncidentStatus.ASSIGNED: [IncidentStatus.IN_PROGRESS, IncidentStatus.REPORTED],
    IncidentStatus.IN_PROGRESS: [IncidentStatus.RESOLVED],
    IncidentStatus.RESOLVED: [IncidentStatus.CLOSED],
    IncidentStatus.CLOSED: [],
    IncidentStatus.REJECTED: [],
}

class IncidentService:
    def __init__(self, db: AsyncSession):
        self.incident_repo = IncidentRepository(db)
        self.db = db
    
    async def create_incident(self, data: IncidentCreate, reporter_id: UUID) -> Incident:
        code = await self.incident_repo.get_next_code()
        
        incident = Incident(
            code=code,
            title=data.title,
            description=data.description,
            category=data.category,
            priority=data.priority or IncidentPriority.LOW,
            status=IncidentStatus.REPORTED,
            latitude=data.latitude,
            longitude=data.longitude,
            address=data.address,
            district=data.district,
            reporter_id=reporter_id
        )
        
        incident = await self.incident_repo.create(incident)
        
        history = IncidentHistory(
            incident_id=incident.id,
            status=IncidentStatus.REPORTED,
            notes="Incident reported",
            created_by_id=reporter_id
        )
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(incident)
        
        return incident
    
    async def get_incident(self, incident_id: UUID) -> Incident:
        incident = await self.incident_repo.get_by_id(incident_id)
        if not incident:
            raise NotFoundException("Incident not found")
        return incident
    
    async def list_incidents(self, filters: dict, page: int, size: int) -> tuple[list[Incident], int]:
        skip = (page - 1) * size
        incidents = await self.incident_repo.get_with_filters(**filters, skip=skip, limit=size)
        total = await self.incident_repo.count_with_filters(**filters)
        return incidents, total
    
    async def update_incident(self, incident_id: UUID, data: IncidentUpdate, user_id: UUID) -> Incident:
        incident = await self.get_incident(incident_id)
        # Check permissions logic can be added here
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(incident, key, value)
            
        return await self.incident_repo.update(incident)
    
    async def update_status(self, incident_id: UUID, data: IncidentStatusUpdate, user_id: UUID) -> Incident:
        incident = await self.get_incident(incident_id)
        
        if data.status not in VALID_TRANSITIONS.get(incident.status, []):
            raise BadRequestException(f"Invalid status transition from {incident.status} to {data.status}")
            
        incident.status = data.status
        incident = await self.incident_repo.update(incident)
        
        history = IncidentHistory(
            incident_id=incident.id,
            status=data.status,
            notes=data.notes or f"Status updated to {data.status.value}",
            created_by_id=user_id
        )
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(incident)
        
        return incident
    
    async def get_my_incidents(self, reporter_id: UUID, page: int, size: int) -> tuple[list[Incident], int]:
        skip = (page - 1) * size
        incidents = await self.incident_repo.get_by_reporter(reporter_id, skip=skip, limit=size)
        total = await self.incident_repo.count_with_filters(reporter_id=reporter_id)
        return incidents, total
    
    async def get_history(self, incident_id: UUID) -> list[IncidentHistory]:
        result = await self.db.execute(
            select(IncidentHistory)
            .where(IncidentHistory.incident_id == incident_id)
            .order_by(IncidentHistory.created_at)
        )
        return list(result.scalars().all())

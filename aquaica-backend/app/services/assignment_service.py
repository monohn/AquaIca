from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.assignment_repository import AssignmentRepository
from app.repositories.incident_repository import IncidentRepository
from app.repositories.user_repository import UserRepository
from app.models.assignment import Assignment, AssignmentStatus
from app.models.incident import IncidentStatus
from app.models.user import UserRole
from app.models.incident_history import IncidentHistory
from app.schemas.assignment import AssignmentCreate, AssignmentStatusUpdate
from app.utils.exceptions import NotFoundException, BadRequestException

class AssignmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.assignment_repo = AssignmentRepository(db)
        self.incident_repo = IncidentRepository(db)
        self.user_repo = UserRepository(db)
    
    async def create_assignment(self, data: AssignmentCreate, assigned_by_id: UUID) -> Assignment:
        incident = await self.incident_repo.get_by_id(data.incident_id)
        if not incident:
            raise NotFoundException("Incident not found")
            
        if incident.status != IncidentStatus.VALIDATED:
            raise BadRequestException("Incident must be VALIDATED to be assigned")
            
        technician = await self.user_repo.get_by_id(data.technician_id)
        if not technician or technician.role != UserRole.TECHNICIAN:
            raise BadRequestException("User is not a valid technician")
            
        assignment = Assignment(
            incident_id=data.incident_id,
            technician_id=data.technician_id,
            notes=data.notes,
            status=AssignmentStatus.PENDING,
            assigned_by_id=assigned_by_id
        )
        
        assignment = await self.assignment_repo.create(assignment)
        
        incident.status = IncidentStatus.ASSIGNED
        await self.incident_repo.update(incident)
        
        history = IncidentHistory(
            incident_id=incident.id,
            status=IncidentStatus.ASSIGNED,
            notes=f"Assigned to technician {technician.id}",
            created_by_id=assigned_by_id
        )
        self.db.add(history)
        await self.db.commit()
        
        return assignment
    
    async def update_status(self, assignment_id: UUID, data: AssignmentStatusUpdate, user_id: UUID) -> Assignment:
        assignment = await self.get_assignment(assignment_id)
        
        # Technician updates their assignment status
        assignment.status = data.status
        if data.notes:
            assignment.notes = data.notes
        assignment = await self.assignment_repo.update(assignment)
        
        incident = await self.incident_repo.get_by_id(assignment.incident_id)
        
        new_incident_status = None
        if data.status == AssignmentStatus.COMPLETED:
            new_incident_status = IncidentStatus.RESOLVED
        elif data.status == AssignmentStatus.IN_PROGRESS:
            new_incident_status = IncidentStatus.IN_PROGRESS
            
        if new_incident_status and incident.status != new_incident_status:
            incident.status = new_incident_status
            await self.incident_repo.update(incident)
            
            history = IncidentHistory(
                incident_id=incident.id,
                status=new_incident_status,
                notes=f"Status updated via assignment update to {data.status.value}",
                created_by_id=user_id
            )
            self.db.add(history)
            await self.db.commit()
            
        return assignment
    
    async def get_technician_assignments(self, technician_id: UUID, status: AssignmentStatus | None, page: int, size: int) -> tuple[list[Assignment], int]:
        skip = (page - 1) * size
        assignments = await self.assignment_repo.get_by_technician(technician_id, status_filter=status, skip=skip, limit=size)
        total = await self.assignment_repo.count_by_technician(technician_id, status)
        return assignments, total
    
    async def get_assignment(self, assignment_id: UUID) -> Assignment:
        assignment = await self.assignment_repo.get_by_id(assignment_id)
        if not assignment:
            raise NotFoundException("Assignment not found")
        return assignment

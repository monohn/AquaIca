from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.incident_repository import IncidentRepository
from app.repositories.assignment_repository import AssignmentRepository
from app.repositories.user_repository import UserRepository
from app.models.user import UserRole
from app.models.assignment import AssignmentStatus
from app.schemas.dashboard import DashboardResponse, HeatmapPoint, TechnicianWorkload, IncidentStats

class DashboardService:
    def __init__(self, db: AsyncSession):
        self.incident_repo = IncidentRepository(db)
        self.assignment_repo = AssignmentRepository(db)
        self.user_repo = UserRepository(db)
    
    async def get_dashboard(self) -> DashboardResponse:
        total = await self.incident_repo.count()
        by_status = await self.incident_repo.get_stats()
        by_category = dict(await self.incident_repo.get_by_category_stats())
        by_district = dict(await self.incident_repo.get_by_district_stats())
        by_priority = dict(await self.incident_repo.get_by_priority_stats())
        
        recent = await self.incident_repo.get_all(skip=0, limit=10)
        
        stats = IncidentStats(
            total=total,
            by_status=by_status,
            by_category=by_category,
            by_district=by_district,
            by_priority=by_priority
        )
        
        return DashboardResponse(stats=stats, recent_incidents=recent)
    
    async def get_heatmap(self) -> list[HeatmapPoint]:
        data = await self.incident_repo.get_heatmap_data()
        return [HeatmapPoint(latitude=lat, longitude=lng, weight=count) for lat, lng, count in data]
    
    async def get_technician_workloads(self) -> list[TechnicianWorkload]:
        technicians = await self.user_repo.get_by_role(UserRole.TECHNICIAN)
        workloads = []
        
        for tech in technicians:
            active = await self.assignment_repo.count_by_technician(tech.id, AssignmentStatus.IN_PROGRESS)
            completed = await self.assignment_repo.count_by_technician(tech.id, AssignmentStatus.COMPLETED)
            
            workloads.append(TechnicianWorkload(
                technician_id=tech.id,
                technician_name=tech.full_name,
                active_assignments=active,
                completed_assignments=completed
            ))
            
        return workloads

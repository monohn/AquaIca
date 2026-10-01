from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.dashboard import DashboardResponse, HeatmapPoint, TechnicianWorkload
from app.services.dashboard_service import DashboardService
from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import UserRole

router = APIRouter()

@router.get("/", response_model=DashboardResponse, dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Obtener estadísticas del dashboard (Solo ADMIN)."""
    service = DashboardService(db)
    return await service.get_dashboard_stats()

@router.get("/heatmap", response_model=List[HeatmapPoint], dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def get_heatmap_data(db: AsyncSession = Depends(get_db)):
    """Obtener datos para el mapa de calor (Solo ADMIN)."""
    service = DashboardService(db)
    return await service.get_heatmap_data()

@router.get("/technicians/workload", response_model=List[TechnicianWorkload], dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def get_technician_workload(db: AsyncSession = Depends(get_db)):
    """Obtener carga de trabajo de técnicos (Solo ADMIN)."""
    service = DashboardService(db)
    return await service.get_technician_workload()

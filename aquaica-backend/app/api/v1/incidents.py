from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Any

from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentStatusUpdate, IncidentResponse, IncidentListResponse
from app.services.incident_service import IncidentService
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.incident import IncidentStatus, IncidentCategory, IncidentPriority

router = APIRouter()

@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role([UserRole.CITIZEN]))])
async def create_incident(
    request: IncidentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Crear una incidencia (Rol CIUDADANO)."""
    service = IncidentService(db)
    return await service.create_incident(request, current_user.id)

@router.get("/", response_model=IncidentListResponse)
async def list_incidents(
    status: Optional[IncidentStatus] = Query(None),
    category: Optional[IncidentCategory] = Query(None),
    priority: Optional[IncidentPriority] = Query(None),
    district: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Listar incidencias (Admin ve todas, Ciudadano las suyas, Técnico las asignadas)."""
    service = IncidentService(db)
    return await service.list_incidents(
        user=current_user,
        status=status,
        category=category,
        priority=priority,
        district=district,
        page=page,
        size=size
    )

@router.get("/my/list", response_model=IncidentListResponse, dependencies=[Depends(require_role([UserRole.CITIZEN]))])
async def list_my_incidents(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener incidencias del usuario actual (Ciudadano)."""
    service = IncidentService(db)
    return await service.list_incidents(user=current_user, page=page, size=size)

@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener detalle de incidencia."""
    service = IncidentService(db)
    return await service.get_incident(incident_id, current_user)

@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: int,
    request: IncidentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualizar incidencia (Reportero o Admin)."""
    service = IncidentService(db)
    return await service.update_incident(incident_id, request, current_user)

@router.patch("/{incident_id}/status", response_model=IncidentResponse, dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def update_incident_status(
    incident_id: int,
    request: IncidentStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualizar estado de incidencia (Solo ADMIN)."""
    service = IncidentService(db)
    return await service.update_incident_status(incident_id, request, current_user)

@router.get("/{incident_id}/history", response_model=List[Any])
async def get_incident_history(
    incident_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener el historial de la incidencia."""
    service = IncidentService(db)
    return await service.get_incident_history(incident_id, current_user)

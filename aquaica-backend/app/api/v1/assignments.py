from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.schemas.assignment import AssignmentCreate, AssignmentUpdate, AssignmentStatusUpdate, AssignmentResponse, AssignmentListResponse
from app.services.assignment_service import AssignmentService
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.assignment import AssignmentStatus

router = APIRouter()

@router.post("/", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def create_assignment(
    request: AssignmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Crear asignación (Solo ADMIN)."""
    service = AssignmentService(db)
    return await service.create_assignment(request, current_user)

@router.get("/", response_model=AssignmentListResponse)
async def list_assignments(
    status: Optional[AssignmentStatus] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Listar asignaciones (Admin ve todas, Técnico las suyas)."""
    service = AssignmentService(db)
    return await service.list_assignments(user=current_user, status=status, page=page, size=size)

@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener detalle de asignación."""
    service = AssignmentService(db)
    return await service.get_assignment(assignment_id, current_user)

@router.patch("/{assignment_id}/status", response_model=AssignmentResponse, dependencies=[Depends(require_role([UserRole.TECHNICIAN]))])
async def update_assignment_status(
    assignment_id: int,
    request: AssignmentStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualizar estado de asignación (Técnico - su propia asignación)."""
    service = AssignmentService(db)
    return await service.update_assignment_status(assignment_id, request, current_user)

@router.put("/{assignment_id}", response_model=AssignmentResponse, dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def update_assignment(
    assignment_id: int,
    request: AssignmentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualizar detalles de asignación (ADMIN)."""
    service = AssignmentService(db)
    return await service.update_assignment(assignment_id, request, current_user)

from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.schemas.evidence import EvidenceResponse, EvidenceListResponse
from app.services.evidence_service import EvidenceService
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.evidence import EvidenceType

router = APIRouter()

@router.post("/upload", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    incident_id: Optional[int] = Form(None),
    assignment_id: Optional[int] = Form(None),
    evidence_type: EvidenceType = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Subir archivo de evidencia."""
    service = EvidenceService(db)
    return await service.upload_evidence(
        file=file,
        evidence_type=evidence_type,
        incident_id=incident_id,
        assignment_id=assignment_id,
        description=description,
        user=current_user
    )

@router.get("/incident/{incident_id}", response_model=EvidenceListResponse)
async def get_incident_evidence(
    incident_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener evidencias para una incidencia."""
    service = EvidenceService(db)
    return await service.get_incident_evidence(incident_id, current_user)

@router.get("/assignment/{assignment_id}", response_model=EvidenceListResponse)
async def get_assignment_evidence(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener evidencias para una asignación."""
    service = EvidenceService(db)
    return await service.get_assignment_evidence(assignment_id, current_user)

@router.delete("/{evidence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evidence(
    evidence_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Eliminar evidencia."""
    service = EvidenceService(db)
    await service.delete_evidence(evidence_id, current_user)

from uuid import UUID
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.evidence_repository import EvidenceRepository
from app.models.evidence import Evidence, EvidenceType
from app.utils.exceptions import NotFoundException
from app.utils.file_handler import save_upload_file, delete_file

class EvidenceService:
    def __init__(self, db: AsyncSession):
        self.evidence_repo = EvidenceRepository(db)
    
    async def upload_evidence(self, file: UploadFile, incident_id: UUID | None, assignment_id: UUID | None, evidence_type: EvidenceType, description: str | None, uploaded_by_id: UUID) -> Evidence:
        folder = str(incident_id) if incident_id else str(assignment_id)
        file_path, file_name, file_type = await save_upload_file(file, f"uploads/{folder}")
        
        evidence = Evidence(
            incident_id=incident_id,
            assignment_id=assignment_id,
            file_path=file_path,
            file_name=file_name,
            file_type=file_type,
            evidence_type=evidence_type,
            description=description,
            uploaded_by_id=uploaded_by_id
        )
        return await self.evidence_repo.create(evidence)
    
    async def get_incident_evidence(self, incident_id: UUID) -> list[Evidence]:
        return await self.evidence_repo.get_by_incident(incident_id)

    async def get_assignment_evidence(self, assignment_id: UUID) -> list[Evidence]:
        return await self.evidence_repo.get_by_assignment(assignment_id)

    async def delete_evidence(self, evidence_id: UUID, user_id: UUID) -> bool:
        evidence = await self.evidence_repo.get_by_id(evidence_id)
        if not evidence:
            raise NotFoundException("Evidence not found")
            
        delete_file(evidence.file_path)
        return await self.evidence_repo.delete(evidence_id)

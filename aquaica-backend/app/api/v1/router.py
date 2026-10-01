from fastapi import APIRouter
from app.api.v1 import auth, users, incidents, assignments, evidence, dashboard

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(users.router, prefix="/users", tags=["Usuarios"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["Incidencias"])
api_router.include_router(assignments.router, prefix="/assignments", tags=["Asignaciones"])
api_router.include_router(evidence.router, prefix="/evidence", tags=["Evidencias"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

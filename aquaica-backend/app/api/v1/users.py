from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.schemas.user import UserResponse, UserUpdate, UserListResponse
from app.services.user_service import UserService
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User, UserRole

router = APIRouter()

@router.get("/", response_model=UserListResponse, dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def list_users(
    role: Optional[UserRole] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Listar usuarios. Requiere rol ADMIN."""
    service = UserService(db)
    return await service.list_users(role=role, page=page, size=size)

@router.get("/technicians/list", response_model=UserListResponse, dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def list_technicians(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Listar todos los técnicos. Requiere rol ADMIN."""
    service = UserService(db)
    return await service.list_users(role=UserRole.TECHNICIAN, page=page, size=size)

@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Obtener usuario por ID. Requiere rol ADMIN."""
    service = UserService(db)
    return await service.get_user_by_id(user_id)

@router.put("/me", response_model=UserResponse)
async def update_me(
    request: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualizar el propio perfil (cualquier usuario autenticado)."""
    service = UserService(db)
    return await service.update_user(current_user.id, request)

@router.patch("/{user_id}/deactivate", response_model=UserResponse, dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def deactivate_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Desactivar usuario. Requiere rol ADMIN."""
    service = UserService(db)
    return await service.deactivate_user(user_id)

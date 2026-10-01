from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.models.user import User, UserRole
from app.schemas.user import UserUpdate
from app.utils.exceptions import NotFoundException

class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
    
    async def get_user(self, user_id: UUID) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    async def update_user(self, user_id: UUID, data: UserUpdate) -> User:
        user = await self.get_user(user_id)
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)
            
        return await self.user_repo.update(user)

    async def list_users(self, role: UserRole | None, page: int, size: int) -> tuple[list[User], int]:
        skip = (page - 1) * size
        if role:
            users = await self.user_repo.get_by_role(role, skip=skip, limit=size)
            total = await self.user_repo.count_by_role(role)
        else:
            users = await self.user_repo.get_all(skip=skip, limit=size)
            total = await self.user_repo.count()
        return users, total

    async def deactivate_user(self, user_id: UUID) -> User:
        user = await self.get_user(user_id)
        user.is_active = False
        return await self.user_repo.update(user)

    async def get_technicians(self, page: int, size: int) -> tuple[list[User], int]:
        return await self.list_users(role=UserRole.TECHNICIAN, page=page, size=size)

from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    """User repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> list[User]:
        """Get users by role with pagination."""
        result = await self.db.execute(
            select(User).where(User.role == role).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_role(self, role: UserRole) -> int:
        """Count users by role."""
        result = await self.db.execute(
            select(func.count()).select_from(User).where(User.role == role)
        )
        return result.scalar() or 0

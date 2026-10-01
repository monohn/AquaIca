from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token
from app.utils.exceptions import BadRequestException, ForbiddenException
from datetime import timedelta

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def register(self, data: RegisterRequest) -> User:
        existing_user = await self.user_repo.get_by_email(data.email)
        if existing_user:
            raise BadRequestException("Email already taken")
        
        user = User(
            email=data.email,
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
            role=data.role,
            phone_number=data.phone_number
        )
        return await self.user_repo.create(user)
    
    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise ForbiddenException("Invalid credentials")
        if not user.is_active:
            raise ForbiddenException("User is deactivated")
            
        access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
        refresh_token = create_refresh_token({"sub": str(user.id), "role": user.role.value})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if not payload:
            raise ForbiddenException("Invalid refresh token")
            
        user_id = payload.get("sub")
        role = payload.get("role")
        
        if not user_id:
            raise ForbiddenException("Invalid refresh token payload")
            
        access_token = create_access_token({"sub": user_id, "role": role})
        new_refresh_token = create_refresh_token({"sub": user_id, "role": role})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )

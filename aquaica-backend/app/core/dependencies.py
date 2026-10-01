"""Authentication and authorization dependencies for FastAPI endpoints."""

from collections.abc import Callable, Coroutine
from typing import Any
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Validate access token and return the authenticated user.

    Args:
        token: Bearer JWT access token from request header.
        db: Asynchronous database session.

    Returns:
        User: Authenticated database user object.

    Raises:
        HTTPException: 401 if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        subject: str | None = payload.get("sub")
        if subject is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        user_uuid = uuid.UUID(subject)
        query = select(User).where(User.id == user_uuid)
    except ValueError:
        query = select(User).where(User.email == subject)

    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account",
        )

    return user


def require_role(
    *roles: UserRole | str,
) -> Callable[[User], Coroutine[Any, Any, User]]:
    """Return a dependency validating that the current user has one of the allowed roles.

    Args:
        *roles: Variable list of permitted roles (UserRole or str).

    Returns:
        Callable: FastAPI dependency ensuring user authorization.
    """
    allowed_roles = {
        r.value if isinstance(r, UserRole) else str(r).upper() for r in roles
    }

    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        user_role = (
            current_user.role.value
            if isinstance(current_user.role, UserRole)
            else str(current_user.role).upper()
        )
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for current user role",
            )
        return current_user

    return role_checker

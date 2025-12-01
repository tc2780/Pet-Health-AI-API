"""
Authentication service for token handling
"""
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.models.user import User
from app.services.user import UserService


async def get_current_user_from_token(token: str, db: AsyncSession) -> User:
    """
    Get current user from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
    
    # Convert string UUID back to UUID object
    try:
        user_id = UUID(user_id_str)
    except (ValueError, AttributeError):
        raise credentials_exception
    
    # Get user from database
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user
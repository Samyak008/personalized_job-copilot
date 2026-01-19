"""
API Dependencies

Common dependencies for API routes (DB session, Authentication).
VALIDATION: Verifies Supabase JWTs.
"""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.config import settings
from app.db import get_db
from app.db.models import User
from app.db.repositories.base import BaseRepository

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",  # Placeholder
    auto_error=True
)

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """
    Verify Supabase JWT and get/create local user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT
        # Supabase uses HS256 by default with the project JWT Secret
        payload = jwt.decode(
            token, 
            settings.supabase_jwt_secret, 
            algorithms=["HS256"],
            audience="authenticated" # Supabase default audience
        )
        
        user_id_str: str = payload.get("sub")
        email: str = payload.get("email")
        
        if not user_id_str or not email:
            raise credentials_exception
            
        user_id = UUID(user_id_str)
        
    except (JWTError, ValueError):
        raise credentials_exception
        
    # Check if user exists in local DB
    repo = BaseRepository(User, db)
    user = await repo.get(user_id)
    
    if not user:
        # Just-in-Time Sync
        # Create user in public.users to match auth.users
        # We put a placeholder for hashed_password since Supabase handles auth
        user = User(
            id=user_id,
            email=email,
            hashed_password="MANAGED_BY_SUPABASE_AUTH"
        )
        user = await repo.create(user)
    
    return user


# Type alias for current user dependency
CurrentUser = Annotated[User, Depends(get_current_user)]
SessionDep = Annotated[AsyncSession, Depends(get_db)]

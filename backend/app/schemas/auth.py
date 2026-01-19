"""
Authentication Schemas

Token and authentication-related Pydantic models.
"""

from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded token data."""
    user_id: Optional[str] = None
    email: Optional[str] = None

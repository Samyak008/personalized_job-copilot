from typing import Annotated, Optional, Dict, Any
from uuid import UUID
import httpx
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import traceback
import json

from app.core.config import settings
from app.db.base import get_db
from app.db.models import User
from app.db.repositories.base import BaseRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWKS Cache
JWKS_CLIENT: Optional[Dict[str, Any]] = None

async def get_supabase_jwks() -> Dict[str, Any]:
    global JWKS_CLIENT
    if JWKS_CLIENT:
        return JWKS_CLIENT
        
    base_url = settings.supabase_url.rstrip('/')
    candidates = [
        "/auth/v1/.well-known/jwks.json", # Standard OIDC under /auth/v1
        "/.well-known/jwks.json",         # Root OIDC
        "/auth/v1/jwks"                   # LegacySupabase
    ]

    async with httpx.AsyncClient() as client:
        for path in candidates:
            jwks_url = f"{base_url}{path}"
            # print(f"Probing JWKS: {jwks_url}")
            try:
                response = await client.get(
                    jwks_url, 
                    headers={"apikey": settings.supabase_key}
                )
                if response.status_code == 200:
                    print(f"JWKS Found at: {jwks_url}")
                    JWKS_CLIENT = response.json()
                    return JWKS_CLIENT
            except Exception as e:
                print(f"Probe failed for {path}: {e}")
                continue
                
        print("!!! JWKS FAILURE: All candidates failed.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Could not fetch auth keys from any known endpoint"
        )

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """
    Verify Supabase JWT (ES256/RS256 via JWKS or HS256 via Secret) and get/create local user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Debug Logging
    # print(f"--- AUTH DEBUG ---")
    # print(f"Token Received: {token[:10] if token else 'NONE'}")
    
    try:
        # Get Header to check Key ID (kid) and Alg
        header = jwt.get_unverified_header(token)
        # print(f"Token Header: {header}")
        
        alg = header.get('alg')
        
        if alg == 'HS256':
             # Fallback to Secret validation if configured for HS256
             payload = jwt.decode(
                token, 
                settings.supabase_jwt_secret, 
                algorithms=["HS256"],
                audience="authenticated"
            )
        else:
            # For ES256 / RS256, use JWKS
            jwks = await get_supabase_jwks()
            
            if not jwks:
                 # Debugging mode: If JWKS failed, print issuer from token
                 claims = jwt.get_unverified_claims(token)
                 print(f"Token Issuer Claim: {claims.get('iss')}")
                 raise credentials_exception

            # Verify signature using the key from JWKS
            
            kid = header.get('kid')
            if not kid:
                print("Missing 'kid' in header")
                raise credentials_exception
                
            key = next((k for k in jwks['keys'] if k['kid'] == kid), None)
            if not key:
                print(f"Key {kid} not found in JWKS")
                # Force refresh JWKS once
                global JWKS_CLIENT
                JWKS_CLIENT = None
                jwks = await get_supabase_jwks()
                if not jwks: raise credentials_exception
                key = next((k for k in jwks['keys'] if k['kid'] == kid), None)
                if not key:
                    raise credentials_exception
            
            payload = jwt.decode(
                token,
                key, # Pass the JWK dict directly, python-jose supports it
                algorithms=[alg],
                audience="authenticated"
            )

        # print("Token Decode: SUCCESS")
        
        user_id_str: str = payload.get("sub")
        email: str = payload.get("email")
        
        if not user_id_str or not email:
            print("Missing sub or email in payload")
            raise credentials_exception
            
        user_id = UUID(user_id_str)
        
    except (JWTError, ValueError) as e:
        print(f"!!! AUTH ERROR (JWT): {e}")
        # print(traceback.format_exc())
        raise credentials_exception
    except Exception as e:
        print(f"!!! AUTH ERROR (Unexpected): {e}")
        print(traceback.format_exc())
        raise credentials_exception
        
    # Check if user exists in local DB
    repo = BaseRepository(User, db)
    user = await repo.get(user_id)
    
    
    if not user:
        try:
            # Just-in-Time Sync
            user = User(
                id=user_id,
                email=email,
                hashed_password="MANAGED_BY_SUPABASE_AUTH"
            )
            user = await repo.create(user)
        except Exception:
            # Handle race condition: User might have been created by a parallel request
            # logging.warning(f"User creation race condition for {user_id}")
            user = await repo.get(user_id)
            if not user:
                 raise HTTPException(status_code=500, detail="Failed to sync user")
    
    return user
    
SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

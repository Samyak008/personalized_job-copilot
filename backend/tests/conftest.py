import sys
import os
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.main import app
from app.api.deps import get_db, get_current_user
from app.db.models import User
from app.core.config import settings



# --- Mock Data Fixtures ---
@pytest.fixture
def mock_user_id():
    return uuid4()

@pytest.fixture
def mock_user(mock_user_id) -> User:
    return User(
        id=mock_user_id,
        email="test@example.com",
        hashed_password="mocked_password_hash"
    )

@pytest.fixture
def mock_db_session():
    """Returns a MagicMock that mimics an AsyncSession."""
    session = AsyncMock()
    # Mock specific session methods/attributes if needed
    return session

# --- API Client Fixture ---
@pytest.fixture
async def client(mock_user, mock_db_session) -> AsyncGenerator[AsyncClient, None]:
    """
    Returns an httpx.AsyncClient with mocked dependencies.
    Authenticates the user by overriding get_current_user.
    """
    async def override_get_db():
        yield mock_db_session

    async def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    
    app.dependency_overrides.clear()

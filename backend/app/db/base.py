"""
Database Base Configuration

Async SQLAlchemy engine and session configuration for Supabase PostgreSQL.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Create async engine for Supabase PostgreSQL
engine = create_async_engine(
    settings.database_url,
    echo=settings.log_level == "DEBUG",  # SQL logging in debug mode
    pool_pre_ping=True,  # Verify connections before use
)

# Async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Declarative base for models
Base = declarative_base()


async def get_db():
    """
    Dependency that provides a database session.
    
    Usage in FastAPI:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

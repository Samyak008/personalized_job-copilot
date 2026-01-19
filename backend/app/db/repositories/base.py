"""
Base Repository

Generic repository pattern for database operations.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import TypeVar, Generic, Type, Optional, List, Any
from uuid import UUID

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations."""

    def __init__(self, model: Type[T], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: UUID) -> Optional[T]:
        """Get a single record by ID."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_field(self, field: str, value: Any) -> Optional[T]:
        """Get a single record by a specific field."""
        column = getattr(self.model, field)
        result = await self.db.execute(
            select(self.model).where(column == value)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        descending: bool = True
    ) -> List[T]:
        """Get all records with pagination."""
        query = select(self.model)
        
        if order_by:
            column = getattr(self.model, order_by)
            query = query.order_by(column.desc() if descending else column.asc())
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[T]:
        """Get all records for a specific user."""
        result = await self.db.execute(
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, obj: T) -> T:
        """Create a new record."""
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update(self, id: UUID, **kwargs) -> Optional[T]:
        """Update a record by ID."""
        await self.db.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
        )
        await self.db.commit()
        return await self.get(id)

    async def delete(self, id: UUID) -> bool:
        """Delete a record by ID."""
        obj = await self.get(id)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()
            return True
        return False

    async def exists(self, id: UUID) -> bool:
        """Check if a record exists."""
        result = await self.get(id)
        return result is not None

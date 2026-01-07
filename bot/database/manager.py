"""Database manager for handling connections and operations."""

from __future__ import annotations

import traceback
from typing import TYPE_CHECKING, Any, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bot.database.models import Base

if TYPE_CHECKING:
    from bot.core.config import BotConfig
    from bot.utils.logger import BotLogger

T = TypeVar("T", bound=Base)


class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self, config: BotConfig, logger: BotLogger):
        """
        Initialize the database manager.

        Args:
            config: Bot configuration
            logger: Bot logger
        """
        self.config = config
        self.logger = logger
        self.engine = None
        self.session_factory: Optional[async_sessionmaker[AsyncSession]] = None

    async def initialize(self) -> None:
        """Initialize database connection and create tables."""
        try:
            self.logger.info(f"Initializing database: {self.config.database_type.value}")

            # Create async engine
            self.engine = create_async_engine(
                self.config.database_url,
                echo=self.config.debug_mode,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
            )

            # Create session factory
            self.session_factory = async_sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )

            # Create all tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            self.logger.info("Database initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            self.logger.error(traceback.format_exc())
            raise

    async def close(self) -> None:
        """Close database connection."""
        if self.engine:
            await self.engine.dispose()
            self.logger.info("Database connection closed")

    def get_session(self) -> AsyncSession:
        """
        Get a new database session.

        Returns:
            AsyncSession for database operations

        Raises:
            RuntimeError: If database is not initialized
        """
        if not self.session_factory:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.session_factory()

    async def get(
            self, model: Type[T], id_value: Any, id_column: str = "id"
    ) -> Optional[T]:
        """
        Get a single record by ID.

        Args:
            model: SQLAlchemy model class
            id_value: Value of the ID to search for
            id_column: Name of the ID column (default: "id")

        Returns:
            Model instance or None if not found
        """
        async with self.get_session() as session:
            stmt = select(model).where(getattr(model, id_column) == id_value)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def create(self, instance: T) -> T:
        """
        Create a new record.

        Args:
            instance: Model instance to create

        Returns:
            Created model instance with updated fields
        """
        async with self.get_session() as session:
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance

    async def update(self, instance: T) -> T:
        """
        Update an existing record.

        Args:
            instance: Model instance to update

        Returns:
            Updated model instance
        """
        async with self.get_session() as session:
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance

    async def delete(self, instance: T) -> None:
        """
        Delete a record.

        Args:
            instance: Model instance to delete
        """
        async with self.get_session() as session:
            await session.delete(instance)
            await session.commit()

    async def get_all(self, model: Type[T], limit: Optional[int] = None) -> list[T]:
        """
        Get all records of a model.

        Args:
            model: SQLAlchemy model class
            limit: Optional limit on number of records

        Returns:
            List of model instances
        """
        async with self.get_session() as session:
            stmt = select(model)
            if limit:
                stmt = stmt.limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def execute_raw(self, query: str, params: Optional[dict] = None) -> Any:
        """
        Execute a raw SQL query.

        Args:
            query: SQL query string
            params: Optional query parameters

        Returns:
            Query result
        """
        async with self.get_session() as session:
            result = await session.execute(query, params or {})
            await session.commit()
            return result

    async def health_check(self) -> bool:
        """
        Check if database connection is healthy.

        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            async with self.get_session() as session:
                await session.execute(select(1))
            return True
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return False

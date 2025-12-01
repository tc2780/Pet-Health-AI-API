"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create async engine for database operations
async_engine = create_async_engine(
    settings.database_url_async,
    echo=settings.debug,
    future=True,
    pool_pre_ping=True,
)

# Create sync engine for migrations and testing
sync_engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    pool_pre_ping=True,
)

# Async session factory
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Sync session factory for migrations
SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)

# Base class for all models
Base = declarative_base()


async def get_db_session() -> AsyncSession:
    """
    Dependency function that yields database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database tables
    """
    async with async_engine.begin() as conn:
        # Import all models to ensure they're registered
        from app.models import user, pet, symptom  # noqa
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    Close database connections
    """
    await async_engine.dispose()
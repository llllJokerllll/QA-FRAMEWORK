from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import logging

from config import settings

logger = logging.getLogger(__name__)

# Determine engine configuration based on database URL
# SQLite doesn't support connection pooling, PostgreSQL does
database_url = settings.async_database_url

if database_url.startswith("sqlite"):
    # SQLite: minimal config, no pooling
    engine = create_async_engine(
        database_url,
        echo=False  # Set to True for SQL debug logging
    )
else:
    # PostgreSQL: connection pooling with health checks
    engine = create_async_engine(
        database_url,
        pool_size=20,
        max_overflow=30,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False  # Set to True for SQL debug logging
    )

# Create async session maker
AsyncSessionFactory = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)


async def init_db():
    """Initialize database connections and create tables"""
    from models import Base
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully")


async def get_db_session():
    """Dependency to get database session"""
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()
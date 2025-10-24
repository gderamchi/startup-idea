"""
Database Session Management
SQLAlchemy engine and session configuration
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Create SQLAlchemy Base class
Base = declarative_base()

# Create synchronous engine
# SQLite doesn't support pool settings, so we conditionally apply them
db_url = settings.get_database_url()
is_sqlite = db_url.startswith("sqlite")

if is_sqlite:
    engine = create_engine(
        db_url,
        echo=settings.DB_ECHO,
        connect_args={"check_same_thread": False},  # Needed for SQLite
    )
else:
    engine = create_engine(
        db_url,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
        echo=settings.DB_ECHO,
        pool_pre_ping=True,  # Verify connections before using
    )

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
)

# Create async engine (for async operations)
# Note: SQLite with aiosqlite for async, PostgreSQL with asyncpg
if is_sqlite:
    async_db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://")
    async_engine = create_async_engine(
        async_db_url,
        echo=settings.DB_ECHO,
        connect_args={"check_same_thread": False},
        poolclass=NullPool,
    )
else:
    async_db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
    async_engine = create_async_engine(
        async_db_url,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
        echo=settings.DB_ECHO,
        poolclass=NullPool if settings.is_testing else None,
    )

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def get_db() -> Session:
    """
    Dependency for getting database session
    Yields a database session and ensures it's closed after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncSession:
    """
    Dependency for getting async database session
    Yields an async database session and ensures it's closed after use
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

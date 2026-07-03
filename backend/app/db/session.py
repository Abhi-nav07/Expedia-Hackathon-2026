"""
Async database session management.

Uses SQLAlchemy 2.0's async engine with connection pooling tuned for
hackathon-scale concurrency (small pool, generous overflow, pre-ping to
avoid stale-connection errors after idle periods).
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_DEBUG,
    pool_pre_ping=True,   # avoids "server closed the connection unexpectedly" after idle
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,    # recycle connections every 30 min
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a request-scoped DB session and
    guarantees it is closed (and rolled back on error) afterward.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

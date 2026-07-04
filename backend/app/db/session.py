"""
Async database session management.

Engine construction branches on the DATABASE_URL scheme so that SQLite
(local/hackathon default) and PostgreSQL/Supabase (production target) each
get their correct driver settings — but this is the ONLY file that needs
to know that. Repositories, services, and models are identical either way.

Migration path to PostgreSQL/Supabase:
  1. Change DATABASE_URL / DATABASE_URL_SYNC in .env to the Postgres/
     Supabase connection string.
  2. Run `alembic upgrade head` against the new database.
  3. Deploy. No application code changes required.
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import settings

_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

if _is_sqlite:
    # SQLite-specific tuning:
    # - check_same_thread=False: required since FastAPI may use the
    #   connection across different async tasks/threads.
    # - StaticPool + single shared connection avoids "database is locked"
    #   errors under concurrent access from a single-file DB in dev.
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.APP_DEBUG,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL / Supabase: real connection pooling, tuned for
    # hackathon-scale concurrency.
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.APP_DEBUG,
        pool_pre_ping=True,  # avoids "server closed the connection unexpectedly" after idle
        pool_size=5,
        max_overflow=10,
        pool_recycle=1800,  # recycle connections every 30 min
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


async def enable_sqlite_foreign_keys() -> None:
    """
    SQLite does not enforce foreign key constraints by default — must be
    turned on per-connection. Call once at app startup when using SQLite.
    No-op on PostgreSQL/Supabase, which enforce FKs natively.
    """
    if not _is_sqlite:
        return
    from sqlalchemy import text

    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA foreign_keys=ON"))

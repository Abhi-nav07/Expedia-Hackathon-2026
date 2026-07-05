"""
Shared pytest fixtures.

Test isolation strategy:
- Each test gets a fresh in-memory SQLite database (StaticPool, single
  connection) with tables created fresh — completely isolated from the
  local dev SQLite file and from other tests.
- Redis is replaced with `FakeRedis`, a minimal in-memory stand-in
  implementing only `setex`/`exists` (all AuthService actually calls it
  for). This is NOT a full Redis simulation — it doesn't enforce TTL
  expiry, for instance — so it's honestly a test double, not a fake
  integration test. Full integration testing against real Redis would
  use docker-compose's redis service; that's a documented future step
  for CI, not implemented here (see docs/07-api-reference.md's "Testing"
  notes).
"""
import os
from typing import AsyncGenerator

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-at-least-32-characters-long")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("DATABASE_URL_SYNC", "sqlite:///:memory:")

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User  # noqa: F401 — ensures the table is registered on Base.metadata


class FakeRedis:
    """Minimal in-memory stand-in for the two Redis operations AuthService
    uses (setex, exists). Not a TTL-accurate simulation — see module docstring."""

    def __init__(self):
        self._store: dict[str, str] = {}

    async def setex(self, key: str, ttl: int, value: str) -> None:
        self._store[key] = value

    async def exists(self, key: str) -> int:
        return 1 if key in self._store else 0


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """
    slowapi's Limiter (app.middleware.rate_limit.limiter) is a
    module-level singleton with in-memory storage — without resetting it,
    request counts accumulate across the ENTIRE pytest session (not just
    within a test), so a test late in the suite can fail because an
    earlier, unrelated test already used up that IP's quota on the same
    endpoint. This was caught by running the actual suite, not by
    reasoning about it beforehand.
    """
    from app.middleware.rate_limit import limiter

    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture
def fake_redis(monkeypatch) -> FakeRedis:
    redis = FakeRedis()
    monkeypatch.setattr("app.services.auth_service.get_redis_client", lambda: redis)
    monkeypatch.setattr("app.api.v1.routers.auth.get_redis_client", lambda: redis)
    return redis


@pytest.fixture
async def test_db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with session_factory() as session:
        yield session

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.fixture
async def client(test_db_session, fake_redis) -> AsyncGenerator[AsyncClient, None]:
    """Depends on test_db_session to guarantee the DB override is applied
    before any request is made through this client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

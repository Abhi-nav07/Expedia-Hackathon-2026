"""
Shared Redis client.

Kept as a single module so every future feature needing caching, rate
limiting, or token revocation reuses one connection pool rather than
each module opening its own. `slowapi`'s rate limiter (middleware/
rate_limit.py) currently uses in-memory storage by default and is
independent of this client — wiring slowapi to Redis for multi-instance
deployments is a documented future step (see docs/07-api-reference.md).
"""
from redis.asyncio import ConnectionPool, Redis

from app.core.config import settings

_pool = ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)


def get_redis_client() -> Redis:
    """Returns a Redis client bound to the shared connection pool.
    Cheap to call repeatedly — does not open a new connection each time."""
    return Redis(connection_pool=_pool)

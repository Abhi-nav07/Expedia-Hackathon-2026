"""
Health check endpoint. Deliberately unauthenticated and lightweight —
used by Docker's HEALTHCHECK, load balancers, and uptime monitors.
Verifies the app can actually reach its dependencies, not just that
the process is alive.
"""
from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db

router = APIRouter(tags=["Health"])


async def get_redis() -> Redis:
    return Redis.from_url(settings.REDIS_URL, decode_responses=True)


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> dict:
    status_report = {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}

    # DB check
    try:
        await db.execute(text("SELECT 1"))
        status_report["database"] = "ok"
    except Exception:
        status_report["database"] = "unreachable"
        status_report["status"] = "degraded"

    # Redis check
    try:
        redis = await get_redis()
        await redis.ping()
        await redis.aclose()
        status_report["redis"] = "ok"
    except Exception:
        status_report["redis"] = "unreachable"
        status_report["status"] = "degraded"

    return status_report

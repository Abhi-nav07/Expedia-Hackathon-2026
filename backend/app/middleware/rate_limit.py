"""
Global rate limiting via slowapi (a Flask-Limiter-style wrapper for Starlette).

Applied as a default limit on every route; individual routers can override
with a stricter limit (e.g. login endpoints) using the @limiter.limit(...)
decorator once this limiter is wired into app.state in main.py.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
    headers_enabled=True,  # sends X-RateLimit-* headers back to the client
)

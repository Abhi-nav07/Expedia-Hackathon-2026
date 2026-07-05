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
    # headers_enabled=True was tried initially (to send informational
    # X-RateLimit-* headers) but slowapi requires every rate-limited
    # endpoint to declare an explicit `response: Response` parameter so
    # it has something to inject headers into. Most endpoints have no
    # other reason to need that parameter (they return a Pydantic model
    # and let FastAPI serialize it), and slowapi throws a hard runtime
    # exception — not a graceful no-op — on any endpoint missing it. This
    # was only caught by actually running a live request through the
    # rate-limited /register endpoint in Module 10's test suite; it would
    # have broken registration in any real deployment. Disabled — rate
    # limiting itself (429 on limit exceeded) is fully unaffected; only
    # the informational response headers are lost.
    headers_enabled=False,
)


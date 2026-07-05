"""
Application entrypoint.

This file only WIRES components together — no business logic lives here.
Each concern (logging, security, rate limiting, exceptions) is defined in
its own module and imported here for composition.
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.routers import auth, health, users
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.db.session import enable_sqlite_foreign_keys
from app.middleware.rate_limit import limiter
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

configure_logging()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.is_sqlite:
        # sqlite+aiosqlite:///./data/app.db -> ensure ./data exists
        db_path = settings.DATABASE_URL.split("///")[-1]
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        await enable_sqlite_foreign_keys()

    # Avatar upload directory (see app/services/user_service.py) must
    # exist before any upload request arrives.
    Path(settings.AVATAR_UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

    logger.info(
        "app_startup",
        env=settings.APP_ENV,
        debug=settings.APP_DEBUG,
        database=settings.DATABASE_URL.split("://")[0],
    )
    yield
    logger.info("app_shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        description=(
            "Adaptive travel-tech hackathon platform — reusable auth, user "
            "profile, and RBAC/permissions infrastructure. See "
            "docs/07-api-reference.md for a human-readable endpoint summary."
        ),
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # --- Rate limiting ---
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)
    app.add_middleware(SlowAPIMiddleware)

    # --- Security & observability middleware (order matters: outermost first) ---
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # --- CORS: explicit allow-list only, no wildcard with credentials ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )

    # --- Exception handlers (safe error responses, never leak internals) ---
    register_exception_handlers(app)

    # --- Static files: uploaded avatars (see user_service.py) ---
    Path(settings.AVATAR_UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    app.mount(
        "/uploads/avatars",
        StaticFiles(directory=settings.AVATAR_UPLOAD_DIR),
        name="avatars",
    )

    # --- Routers ---
    app.include_router(health.router)
    app.include_router(health.router, prefix=settings.API_V1_PREFIX)
    app.include_router(
        auth.router,
        prefix=settings.API_V1_PREFIX + "/auth",
        tags=["Authentication"],
    )
    app.include_router(
        users.router,
        prefix=settings.API_V1_PREFIX + "/users",
        tags=["Users"],
    )
    # Future routers (hotels, flights, bookings, etc.) register here once
    # the challenge is known.

    return app


async def _rate_limit_handler(request, exc: RateLimitExceeded):
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "code": "RATE_LIMITED",
                "message": "Too many requests, please slow down.",
            }
        },
    )


app = create_app()

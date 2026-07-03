# Patch for backend/app/main.py (from Module 2)

Apply these two changes to the existing `main.py`:

--------------------------------------------------------------------------
1. Add the import, alongside the existing health import:

    from app.api.v1.routers import health
    from app.api.v1.routers import auth          # <-- add this line

--------------------------------------------------------------------------
2. Replace this block:

    # --- Routers ---
    app.include_router(health.router)
    app.include_router(health.router, prefix=settings.API_V1_PREFIX)
    # Future routers (auth, users, etc.) register here as they're built,
    # e.g.: app.include_router(auth.router, prefix=settings.API_V1_PREFIX + "/auth", tags=["Auth"])

   with:

    # --- Routers ---
    app.include_router(health.router)
    app.include_router(health.router, prefix=settings.API_V1_PREFIX)
    app.include_router(
        auth.router,
        prefix=settings.API_V1_PREFIX + "/auth",
        tags=["Auth"],
    )
    # Future routers (users, hotels, flights, etc.) register here as they're built.

--------------------------------------------------------------------------
No other changes to main.py are needed — CORS, rate limiting, security
headers, and exception handling from Module 2 already cover the new
/auth/* routes automatically since they're applied at the app level.

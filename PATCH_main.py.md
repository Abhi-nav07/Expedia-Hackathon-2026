# Patch for backend/app/main.py

Two small additions needed to fully wire up SQLite.

--------------------------------------------------------------------------
1. Add these imports near the top, with the other app imports:

    from pathlib import Path

    from app.db.session import enable_sqlite_foreign_keys

--------------------------------------------------------------------------
2. Update the `lifespan` function to ensure the SQLite data directory
   exists and foreign keys are enabled before the app starts serving
   requests. Replace:

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("app_startup", env=settings.APP_ENV, debug=settings.APP_DEBUG)
        yield
        logger.info("app_shutdown")

   with:

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if settings.is_sqlite:
            # sqlite+aiosqlite:///./data/app.db -> ensure ./data exists
            db_path = settings.DATABASE_URL.split("///")[-1]
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            await enable_sqlite_foreign_keys()

        logger.info(
            "app_startup",
            env=settings.APP_ENV,
            debug=settings.APP_DEBUG,
            database=settings.DATABASE_URL.split("://")[0],
        )
        yield
        logger.info("app_shutdown")

--------------------------------------------------------------------------
No other changes needed. This combines with the auth router patch from
Module 3 (PATCH_main.py.md) — apply both to the same file.

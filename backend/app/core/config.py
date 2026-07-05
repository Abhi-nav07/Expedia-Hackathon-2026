"""
Centralized application configuration.

All environment-dependent values must be read through this module.
Never call os.getenv() directly elsewhere in the codebase — this keeps
configuration auditable and prevents secrets from leaking into random files.

DATABASE PORTABILITY: DATABASE_URL / DATABASE_URL_SYNC default to a local
SQLite file, which is all a hackathon needs — no DB container, no waiting
on Postgres to become healthy. To move to PostgreSQL or Supabase later,
only these two values change (in .env); nothing else in the codebase
references a specific database backend. See app/db/session.py and
app/db/types.py for the two places that branch on dialect.
"""
from functools import lru_cache
from typing import List, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- App ---
    APP_ENV: Literal["local", "staging", "production"] = "local"
    APP_NAME: str = "Expedia-Hackathon-2026"
    APP_DEBUG: bool = True
    APP_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"

    # --- API ---
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_PORT: int = 8000

    # --- Database ---
    # Default: local SQLite file under ./data/. Swap to a PostgreSQL or
    # Supabase connection string here (or via .env) with no other code
    # changes required.
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/app.db"
    DATABASE_URL_SYNC: str = "sqlite:///./data/app.db"

    # --- Redis ---
    REDIS_URL: str = "redis://redis:6379/0"

    # --- JWT / Security ---
    JWT_SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_HASH_SCHEME: str = "argon2"

    # --- Password reset / email verification tokens ---
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24

    # --- Email ---
    EMAIL_PROVIDER: Literal["console"] = "console"

    # --- Avatar upload ---
    AVATAR_MAX_SIZE_MB: int = 5
    AVATAR_UPLOAD_DIR: str = "./data/avatars"

    # --- CORS ---
    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000"

    # --- Rate limiting ---
    RATE_LIMIT_PER_MINUTE: int = 60

    # --- OAuth ---
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    OAUTH_REDIRECT_URL: str = "http://localhost:8000/api/v1/auth/oauth/callback"

    # --- AI ---
    AI_PROVIDER: Literal["openai", "gemini", "claude"] = "openai"
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    AI_MODEL_NAME: str = "gpt-4o-mini"
    AI_MAX_TOKENS: int = 1024
    AI_REQUEST_TIMEOUT_SECONDS: int = 30

    # --- Vector DB ---
    VECTOR_DB_PROVIDER: str = "pgvector"
    VECTOR_DB_URL: str = ""

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_secret_not_placeholder(cls, v: str) -> str:
        """Fail fast in production if someone forgot to set a real secret."""
        if v.startswith("CHANGE_ME"):
            raise ValueError(
                "JWT_SECRET_KEY is still a placeholder. "
                "Generate one with: openssl rand -hex 32"
            )
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings accessor. FastAPI dependencies should inject this
    rather than instantiating Settings() directly, so config is read once.
    """
    return Settings()


settings = get_settings()

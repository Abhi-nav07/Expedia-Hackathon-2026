FROM python:3.12-slim AS base

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# gcc is kept for argon2-cffi's C extension build; curl for the healthcheck.
# libpq-dev intentionally omitted — not needed while SQLite is the active
# driver. If you uncomment asyncpg/psycopg2-binary in requirements.txt to
# move to PostgreSQL/Supabase, add `libpq-dev` back to this apt-get line.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# SQLite data directory, owned by the non-root app user
RUN mkdir -p /app/data

# Security: run as non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser \
    && chown -R appuser:appgroup /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Expedia-Hackathon-2026 — Travel-Tech Starter Kit

A modular, production-grade starter kit for the Expedia Campus Hackathon, built to be adapted to nearly any travel-tech problem statement within hours, not days.

## Stack
- **Frontend**: Next.js 14 (14.2.35 — patched, see `docs/`), TypeScript, Tailwind CSS, ShadCN-style components, Framer Motion, React Query, React Hook Form, Zod, Zustand
- **Backend**: FastAPI, SQLAlchemy (async), Alembic, SQLite (local default, portable to PostgreSQL/Supabase with a 2-line `.env` change — see `docs/05-database-portability.md`), Redis, JWT with refresh-token rotation
- **AI**: Provider-agnostic (OpenAI / Gemini / Claude) — not yet implemented, config-ready only
- **DevOps**: Docker, Docker Compose, GitHub Actions (planned), Vercel/Railway/Render/AWS ready

## Quick Start
```bash
git clone <repo>
cd Expedia-Hackathon-2026
cp .env.example .env
# generate a real secret and paste into .env:
openssl rand -hex 32
docker-compose up --build
```
Frontend: http://localhost:3000
Backend docs (Swagger): http://localhost:8000/docs
Backend health check: http://localhost:8000/health

## Backend: what's real right now

As of Module 10, the backend is a fully working, tested authentication +
user-profile platform — not scaffolding:

- **Auth**: register, login (with account lockout), refresh with token
  rotation, logout, change password, forgot/reset password, email
  verification. See `docs/07-api-reference.md` for the full endpoint list.
- **Users**: profile update, preferences (free-form JSON, merge
  semantics), avatar upload (validated, server-generated filenames).
- **RBAC + permissions**: role-based guards (`user`/`admin`/`partner`)
  plus a finer-grained permission layer (`app/core/permissions.py`).
- **33 passing tests** (`backend/tests/`) covering auth, users, security
  primitives, and permissions — run with:
  ```bash
  cd backend
  pip install -r requirements.txt
  JWT_SECRET_KEY=$(openssl rand -hex 32) pytest -v
  ```

### Running backend migrations
```bash
docker-compose exec backend alembic upgrade head
```

## Documentation
See `/docs` for architecture, standards, roadmap, database portability,
the design system, and the full API reference:
- `01-folder-structure.md` — locked repo layout
- `02-architecture.md` — clean architecture, auth flow, deployment flow
- `03-standards.md` — coding conventions
- `04-roadmap.md` — phase-by-phase plan
- `05-database-portability.md` — SQLite <-> PostgreSQL/Supabase
- `06-design-system.md` — frontend tokens, typography, motion
- `07-api-reference.md` — every backend endpoint, request/response shapes, known limitations

## Status
This is a living starter kit, built module-by-module with each module
verified by actually running the code (not just reasoning about it) —
several real bugs (a JWT timestamp-encoding bug that silently broke
every token verification, a rate-limiter/middleware incompatibility, a
SQLite timezone-naive datetime gotcha) were caught this way during
Module 10 and are documented in that module's notes rather than hidden.

See `docs/04-roadmap.md` for the overall phase plan and the latest
module handoff for exactly what's built vs. still pending.

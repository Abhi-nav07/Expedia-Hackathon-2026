# Database Portability: SQLite → PostgreSQL / Supabase

## Current state

The platform runs on **SQLite** by default (`./data/app.db`, mounted as a
Docker volume). This was chosen for the hackathon phase specifically
because it requires no database container, no waiting on a `depends_on`
healthcheck, and no connection-string juggling across teammates' machines
— clone, `docker-compose up`, done.

## What makes this swappable with (almost) zero code changes

The architecture isolates every database-specific concern into exactly
**two files**:

| File | What it does |
|---|---|
| `app/db/session.py` | Branches on `DATABASE_URL`'s scheme to build the right async engine (SQLite: `StaticPool` + `check_same_thread=False`; PostgreSQL/Supabase: real connection pooling with `pool_pre_ping`). |
| `app/db/types.py` | `GUID` — a `TypeDecorator` that always stores UUIDs as `CHAR(36)` (canonical hyphenated string), on every dialect. This is deliberate: it matches exactly what the Alembic migration creates on every backend, so there's no mismatch between the ORM's expectations and the actual column type on a fresh PostgreSQL/Supabase deploy. The tradeoff is not using PostgreSQL's native `UUID` type/indexing — a reasonable cost for guaranteed portability at hackathon scale. |

Everything above those two files — **models, repositories, services,
schemas, routers** — imports `Base`, `GUID`, and `get_db()` and has no
idea what database is actually running. That's intentional: it's the same
principle as the Router → Service → Repository → DB dependency direction
from `docs/02-architecture.md`, extended one layer further down.

Additionally, `role` (and any future enum columns) use
`sa.Enum(..., native_enum=False)`, which SQLAlchemy renders as a
`VARCHAR` + `CHECK` constraint on every backend — avoiding PostgreSQL's
`CREATE TYPE ... AS ENUM`, which has no SQLite equivalent and would
otherwise break portability.

## Migration steps (when you're ready to move to PostgreSQL or Supabase)

1. **Update `.env`** — change two values (examples already commented in
   `.env.example`):
   ```bash
   # PostgreSQL
   DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:5432/DBNAME
   DATABASE_URL_SYNC=postgresql+psycopg2://USER:PASSWORD@HOST:5432/DBNAME

   # Supabase
   DATABASE_URL=postgresql+asyncpg://postgres:PASSWORD@db.PROJECT_REF.supabase.co:5432/postgres
   DATABASE_URL_SYNC=postgresql+psycopg2://postgres:PASSWORD@db.PROJECT_REF.supabase.co:5432/postgres
   ```

2. **Uncomment the Postgres drivers** in `backend/requirements.txt`:
   ```
   asyncpg==0.29.0
   psycopg2-binary==2.9.9
   ```
   and rebuild: `docker-compose build backend`.
   (If running in Docker, also add `libpq-dev` back to `backend/Dockerfile`'s
   `apt-get install` line — noted inline in that file.)

3. **Run migrations against the new database:**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```
   The existing migration (`0001_create_users_table.py`) was written
   without any PostgreSQL-only or SQLite-only types, so it applies
   identically to either backend.

4. **If using Supabase specifically:** Supabase is just managed
   PostgreSQL, so nothing beyond the connection string changes. Row
   Level Security policies, if you want them, are configured in the
   Supabase dashboard / SQL editor — they sit alongside, not instead of,
   this app's own auth checks (defense in depth), and are unaffected
   by anything in this codebase.

5. **Remove the SQLite volume** from `docker-compose.yml` (`sqlite_data`)
   once you've confirmed the new database is live, and optionally
   reintroduce a `db` service if self-hosting PostgreSQL rather than
   using Supabase's managed instance.

## What does NOT change

- `app/models/*.py` — zero edits.
- `app/repositories/*.py` — zero edits.
- `app/services/*.py` — zero edits.
- `app/schemas/*.py` — zero edits.
- `app/api/v1/routers/*.py` — zero edits.
- Alembic migration files already written — zero edits, they replay
  cleanly against PostgreSQL.

## Known SQLite-specific limitations (while in local/hackathon mode)

- **Single-writer concurrency**: SQLite serializes writes. Fine for a
  hackathon demo and even moderate judging-day traffic; not intended for
  real concurrent production load — that's precisely what the Postgres/
  Supabase swap above is for.
- **Foreign keys** are off by default in SQLite; `enable_sqlite_foreign_keys()`
  in `app/db/session.py` turns them on at startup so referential integrity
  is still enforced during local development.
- **No native array/JSONB types** the way PostgreSQL has — if a future
  module needs those (e.g. storing embeddings or tags), prefer a
  SQLAlchemy `JSON` column, which SQLAlchemy maps to `TEXT` on SQLite and
  `JSONB` on PostgreSQL transparently.

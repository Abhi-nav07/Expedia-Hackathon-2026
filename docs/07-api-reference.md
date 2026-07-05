# API Reference (Module 10)

Interactive docs are always the source of truth: `/docs` (Swagger UI) and
`/redoc`, both auto-generated from the code — every endpoint below has a
`summary`, `description`, and typed request/response models in the actual
router source. This file is a quick human-readable index alongside that.

## Authentication (`/api/v1/auth`)

| Method | Path | Auth required | Rate limit | Notes |
|---|---|---|---|---|
| POST | `/register` | No | 10/min | Creates account. Does NOT log in — call `/login` after. |
| POST | `/login` | No | 5/min | Sets httpOnly `refresh_token` cookie; returns access token in body. 5 failed attempts locks the account 15 min. |
| POST | `/refresh` | Cookie or body | 20/min | Rotates refresh token — old one is immediately revoked (Redis-tracked). |
| GET | `/me` | Bearer | — | Current user profile. |
| POST | `/logout` | Bearer | — | Clears cookie; revokes the current refresh token's jti if present. |
| POST | `/change-password` | Bearer | 5/min | Requires current password. |
| POST | `/forgot-password` | No | 5/min | Always 202, regardless of whether the email exists (anti-enumeration). |
| POST | `/reset-password` | Token (body) | 5/min | Consumes the emailed reset token. |
| POST | `/resend-verification` | Bearer | 5/min | No-ops if already verified. |
| POST | `/verify-email` | Token (body) | — | Consumes the emailed verification token. |

## Users (`/api/v1/users`)

| Method | Path | Auth required | Notes |
|---|---|---|---|
| GET | `/me` | Bearer | Same data as `/auth/me`, grouped under REST-conventional `/users`. |
| PATCH | `/me` | Bearer | Partial update. Currently: `full_name`. |
| GET | `/me/preferences` | Bearer | Free-form JSON blob. |
| PUT | `/me/preferences` | Bearer | Shallow-merges into existing preferences — omitted fields are untouched, not cleared. |
| POST | `/me/avatar` | Bearer | Multipart upload. JPEG/PNG/WebP only, up to AVATAR_MAX_SIZE_MB. Server generates the filename — client filename is never trusted. |

## Health (unauthenticated, unversioned + versioned)

| Method | Path | Notes |
|---|---|---|
| GET | `/health` and `/api/v1/health` | Checks live DB and Redis connectivity. |

## Authentication flow (how the pieces fit together)

1. `POST /register` — account created, `is_email_verified=false`.
2. `POST /login` — `refresh_token` httpOnly cookie set (scoped to `/api/v1/auth/refresh`, `SameSite=Strict`), access token (15 min default) returned in the JSON body.
3. Frontend keeps the access token in memory only (see frontend `store/auth-store.ts`) and attaches it as `Authorization: Bearer <token>`.
4. On a 401, the frontend calls `POST /refresh` (cookie sent automatically) — this rotates the refresh token: the old one is revoked (Redis, TTL = its remaining lifetime), a new access+refresh pair is issued.
5. `POST /logout` clears the cookie and revokes that refresh token's jti immediately, rather than waiting for it to expire naturally.

## Password reset / email verification flow

Both follow the same shape: a short-lived, single-purpose JWT
(`TokenType.PASSWORD_RESET` / `TokenType.EMAIL_VERIFICATION`, distinct
from access/refresh tokens — see `core/security.py`) is generated,
embedded in a URL, and "sent" via `EmailService` (currently
`ConsoleEmailService`, which logs the URL rather than emailing it — see
`core/email.py` for how to wire a real provider later).

```
POST /forgot-password {email}
  -> (if account exists) token generated, URL logged
  -> always returns 202 regardless

POST /reset-password {token, new_password}
  -> validates token type + expiry, sets new password, clears any lockout
```

```
POST /resend-verification (authenticated)
  -> token generated, URL logged (no-op if already verified)

POST /verify-email {token}
  -> validates token type + expiry, sets is_email_verified=true
```

## Roles & Permissions

- **Roles** (`app.models.user.UserRole`): `user`, `admin`, `partner`. Enforced via `require_role(...)` (`api/v1/deps.py`).
- **Permissions** (`app.core.permissions`): a finer-grained layer on top — `Permission.USERS_READ`, `USERS_WRITE`, `USERS_READ_ALL`, `ADMIN_FULL`, mapped per role in `ROLE_PERMISSIONS`. Enforced via `require_permission(...)`.
- **Not yet consumed by any endpoint** — this module ships the mechanism (and tests for the mapping logic), not a feature that needs it yet. Use `require_permission(Permission.X)` as a route dependency once a future module needs finer-grained gating than "is this user an admin."

## Testing

Run from `backend/`:
```bash
pip install -r requirements.txt
JWT_SECRET_KEY=$(openssl rand -hex 32) pytest -v
```
- Each test gets an isolated in-memory SQLite DB (fresh tables every test).
- Redis is replaced with a minimal in-memory test double (`tests/conftest.py:FakeRedis`) — not a full Redis simulation (no real TTL expiry). Full integration testing against real Redis (e.g. in CI via docker-compose's `redis` service) is a documented future step, not implemented here.
- The rate limiter is reset before/after every test (`reset_rate_limiter` autouse fixture) — without this, slowapi's in-memory counters persist across the whole pytest session and cause unrelated test failures. This was discovered by actually running the suite, not anticipated in advance.

## Known limitations (honest, not hidden)

- **Email is console-only.** No real provider is wired up. Password reset and email verification are fully functional end-to-end in tests (the "email" is just logged), but nothing is actually delivered to a real inbox yet.
- **Refresh token theft detection is partial.** Rotation means a stolen token is only usable until the legitimate client's next refresh — but there's no active alerting when a revoked token is presented (it's just rejected with 401). Real theft-detection (flag-and-notify) is a future step.
- **Permissions layer has no live consumer yet** (see above) — infrastructure ahead of a feature, by design, per the adaptive-platform brief.
- **Avatar storage is local disk**, not S3/cloud storage — fine for a single-instance hackathon deployment, would need to change for horizontal scaling.
- **slowapi rate limiting is in-memory**, not Redis-backed — fine for a single backend instance; would need `storage_uri=settings.REDIS_URL` passed to `Limiter(...)` for correctness across multiple instances.

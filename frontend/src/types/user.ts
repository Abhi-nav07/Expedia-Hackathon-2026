/**
 * Types mirroring backend/app/schemas/auth.py.
 *
 * These are maintained by hand for now (no OpenAPI codegen step yet).
 * If a future module adds one (e.g. openapi-typescript), this file
 * becomes generated rather than hand-written — the shape should stay
 * identical either way.
 *
 * NOTE: avatar_url was added in Module 11 to match Module 10's backend
 * addition (UserRead.avatar_url) — this file had drifted out of sync
 * with the backend schema since Module 5 first wrote it, caught only
 * when Module 11 actually tried to display an avatar and hit a type
 * error. Worth remembering: any future backend schema change needs the
 * matching edit here too, since nothing currently enforces this
 * automatically.
 */

export type UserRole = "user" | "admin" | "partner";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  is_email_verified: boolean;
  avatar_url: string | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ApiErrorPayload {
  error: {
    code: string;
    message: string;
    correlation_id: string;
    details?: Record<string, unknown>;
  };
}

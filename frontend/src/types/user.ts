/**
 * Types mirroring backend/app/schemas/auth.py.
 *
 * These are maintained by hand for now (no OpenAPI codegen step yet).
 * If a future module adds one (e.g. openapi-typescript), this file
 * becomes generated rather than hand-written — the shape should stay
 * identical either way.
 */

export type UserRole = "user" | "admin" | "partner";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  is_email_verified: boolean;
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

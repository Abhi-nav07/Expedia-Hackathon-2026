import { useAuthStore } from "@/store/auth-store";
import type { ApiErrorPayload, TokenResponse } from "@/types/user";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly correlationId: string;
  readonly details: Record<string, unknown>;

  constructor(status: number, payload: ApiErrorPayload["error"]) {
    super(payload.message);
    this.name = "ApiError";
    this.status = status;
    this.code = payload.code;
    this.correlationId = payload.correlation_id;
    this.details = payload.details ?? {};
  }
}

interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  /** Skip the automatic refresh-and-retry-once behavior (used by the
   * refresh call itself, to avoid infinite recursion). */
  skipAuthRetry?: boolean;
}

let refreshPromise: Promise<string | null> | null = null;

/**
 * Calls /auth/refresh using the httpOnly refresh-token cookie (sent
 * automatically by the browser via credentials: "include"). Deduplicates
 * concurrent refresh attempts — if five requests 401 at once, only one
 * network call to /auth/refresh happens.
 */
async function refreshAccessToken(): Promise<string | null> {
  if (refreshPromise) return refreshPromise;

  refreshPromise = (async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
      });
      if (!res.ok) return null;

      const data: TokenResponse = await res.json();
      useAuthStore.getState().setAuth(data.access_token, data.user);
      return data.access_token;
    } catch {
      return null;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { body, skipAuthRetry, headers, ...rest } = options;
  const accessToken = useAuthStore.getState().accessToken;

  const doFetch = (token: string | null) =>
    fetch(`${API_BASE_URL}${path}`, {
      ...rest,
      credentials: "include", // sends the httpOnly refresh cookie when needed
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...headers,
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });

  let response = await doFetch(accessToken);

  if (response.status === 401 && !skipAuthRetry) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      response = await doFetch(newToken);
    } else {
      useAuthStore.getState().clearAuth();
    }
  }

  if (!response.ok) {
    let payload: ApiErrorPayload["error"] = {
      code: "UNKNOWN_ERROR",
      message: "Something went wrong. Please try again.",
      correlation_id: "",
    };
    try {
      const parsed: ApiErrorPayload = await response.json();
      payload = parsed.error;
    } catch {
      // response body wasn't JSON — fall back to the generic message above
    }
    throw new ApiError(response.status, payload);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const apiClient = {
  get: <T>(path: string, options?: RequestOptions) =>
    request<T>(path, { ...options, method: "GET" }),

  post: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>(path, { ...options, method: "POST", body }),

  put: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>(path, { ...options, method: "PUT", body }),

  patch: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>(path, { ...options, method: "PATCH", body }),

  delete: <T>(path: string, options?: RequestOptions) =>
    request<T>(path, { ...options, method: "DELETE" }),
};

/**
 * Call once on app boot (see app/providers.tsx) to silently attempt a
 * token refresh using the httpOnly cookie, so a page reload doesn't force
 * a re-login if the refresh token is still valid.
 */
export async function bootstrapAuth(): Promise<void> {
  await refreshAccessToken();
}

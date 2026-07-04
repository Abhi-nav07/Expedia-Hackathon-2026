import { create } from "zustand";

import type { User } from "@/types/user";

interface AuthState {
  accessToken: string | null;
  user: User | null;
  isAuthenticated: boolean;
  setAuth: (accessToken: string, user: User) => void;
  clearAuth: () => void;
}

/**
 * Sets/clears a same-origin, non-httpOnly marker cookie that
 * middleware.ts reads for route-protection UX. It carries no secret —
 * just a boolean flag — since the actual refresh token stays httpOnly
 * on the backend's origin and is never readable from the frontend. See
 * the long comment in middleware.ts for why this two-cookie split
 * exists (cross-origin cookie visibility).
 */
function setSessionMarker(active: boolean) {
  if (typeof document === "undefined") return; // SSR guard
  document.cookie = active
    ? "has_session=true; path=/; max-age=604800; samesite=lax"
    : "has_session=; path=/; max-age=0; samesite=lax";
}

/**
 * Deliberately NOT persisted via zustand/middleware's `persist` — the
 * access token must never land in localStorage/sessionStorage, since
 * either is readable by any injected script (XSS). It lives only in this
 * in-memory store for the lifetime of the tab. The refresh token lives
 * server-side in an httpOnly cookie (see backend auth router) and is what
 * survives a page reload; on reload, the API client silently calls
 * /auth/refresh once to repopulate this store. See lib/api/client.ts.
 */
export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  user: null,
  isAuthenticated: false,
  setAuth: (accessToken, user) => {
    setSessionMarker(true);
    set({ accessToken, user, isAuthenticated: true });
  },
  clearAuth: () => {
    setSessionMarker(false);
    set({ accessToken: null, user: null, isAuthenticated: false });
  },
}));

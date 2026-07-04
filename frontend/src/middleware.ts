import { NextResponse, type NextRequest } from "next/server";

/**
 * Route protection heuristic.
 *
 * IMPORTANT — this checks a `has_session` marker cookie, NOT the backend's
 * `refresh_token` cookie. The backend (localhost:8000 in dev) sets
 * `refresh_token` scoped to its own origin; the frontend (localhost:3000)
 * and this middleware run on a different origin/port and would never see
 * that cookie on requests to /dashboard etc. — cookies don't cross
 * origins just because a fetch with credentials:"include" was made
 * earlier. `has_session` is a plain, non-httpOnly, non-sensitive boolean
 * marker set by the frontend itself (see lib/api/client.ts) immediately
 * after a successful login/refresh, purely so this middleware has
 * something to check same-origin. It carries no secret and grants no
 * access on its own.
 *
 * This is still only a UX optimization (avoid flashing a protected page
 * before redirecting to /login) — NOT the real security boundary. The
 * actual enforcement is: every protected API call goes through
 * lib/api/client.ts, which attaches the Bearer token and gets a 401 from
 * FastAPI's get_current_user dependency (see backend/app/api/v1/deps.py)
 * if the token is missing, expired, or invalid. Never rely on this
 * middleware alone to protect sensitive data or actions.
 */
const PROTECTED_PREFIXES = [
  "/dashboard",
  "/analytics",
  "/admin",
  "/settings",
  "/bookings",
  "/wishlist",
  "/profile",
  "/notifications",
];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const isProtected = PROTECTED_PREFIXES.some((prefix) =>
    pathname.startsWith(prefix)
  );
  if (!isProtected) {
    return NextResponse.next();
  }

  const hasSession = request.cookies.get("has_session")?.value === "true";
  if (!hasSession) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/analytics/:path*",
    "/admin/:path*",
    "/settings/:path*",
    "/bookings/:path*",
    "/wishlist/:path*",
    "/profile/:path*",
    "/notifications/:path*",
  ],
};

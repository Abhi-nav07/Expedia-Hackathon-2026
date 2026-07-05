const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

/**
 * The backend serves avatars via a static mount at the root
 * (/uploads/avatars/...), not under /api/v1 like every other endpoint.
 * This strips the /api/v1 suffix so avatar URLs resolve correctly.
 */
export function getBackendOrigin(): string {
  return API_BASE_URL.replace(/\/api\/v1\/?$/, "");
}

/**
 * Resolves the relative avatar_url the backend returns (e.g.
 * "/uploads/avatars/xxx.jpg") into an absolute URL the <Avatar>
 * component can actually load. Already-absolute URLs pass through
 * unchanged (defensive, in case a future provider returns a full CDN URL).
 */
export function resolveAvatarUrl(avatarUrl: string | null | undefined): string | undefined {
  if (!avatarUrl) return undefined;
  if (avatarUrl.startsWith("http://") || avatarUrl.startsWith("https://")) return avatarUrl;
  return `${getBackendOrigin()}${avatarUrl}`;
}

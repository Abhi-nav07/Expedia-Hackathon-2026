/**
 * Derives 1-2 uppercase initials from a full name, for avatar fallbacks.
 * Extracted here since components/layout/navbar.tsx and
 * components/travel/review-card.tsx each had this logic duplicated
 * inline — a third call site (the profile page) made the duplication
 * worth removing rather than copy-pasting a fourth time.
 */
export function getInitialsFromName(name: string | undefined): string {
  if (!name) return "?";
  const parts = name.trim().split(/\s+/);
  const first = parts[0]?.[0] ?? "";
  const last = parts.length > 1 ? parts[parts.length - 1]?.[0] ?? "" : "";
  return (first + last).toUpperCase();
}

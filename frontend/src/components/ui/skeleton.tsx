import type * as React from "react";

import { cn } from "@/lib/utils/cn";

/**
 * Skeleton loading placeholder. Per the performance requirements
 * (docs/*, DevOps module), skeletons are preferred over blocking
 * spinners for list/card content — they communicate layout and
 * perceived speed better. Use `Spinner` (spinner.tsx) instead only for
 * small inline/button loading states.
 */
function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-muted", className)}
      role="status"
      aria-label="Loading"
      {...props}
    />
  );
}

export { Skeleton };

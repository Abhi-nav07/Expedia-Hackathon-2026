import { Loader2 } from "lucide-react";
import type * as React from "react";

import { cn } from "@/lib/utils/cn";

export interface SpinnerProps extends React.SVGAttributes<SVGSVGElement> {
  size?: "sm" | "default" | "lg";
  /** Accessible label announced to screen readers — customize for context, e.g. "Loading bookings". */
  label?: string;
}

const SIZE_MAP: Record<NonNullable<SpinnerProps["size"]>, string> = {
  sm: "h-4 w-4",
  default: "h-6 w-6",
  lg: "h-10 w-10",
};

function Spinner({ className, size = "default", label = "Loading", ...props }: SpinnerProps) {
  return (
    <span role="status" aria-label={label} className="inline-flex">
      <Loader2 className={cn("animate-spin text-primary", SIZE_MAP[size], className)} {...props} />
      <span className="sr-only">{label}</span>
    </span>
  );
}

export { Spinner };

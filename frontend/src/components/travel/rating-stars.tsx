"use client";

import { Star } from "lucide-react";
import * as React from "react";

import { cn } from "@/lib/utils/cn";

export interface RatingStarsProps {
  /** 0-5, supports half-star precision (e.g. 3.5) in read-only mode. */
  value: number;
  /** Enables click-to-rate. When set, `value` is whole-star only (no halves on input). */
  onChange?: (value: number) => void;
  size?: "sm" | "default" | "lg";
  showValue?: boolean;
  className?: string;
}

const SIZE_MAP: Record<NonNullable<RatingStarsProps["size"]>, string> = {
  sm: "h-3.5 w-3.5",
  default: "h-4 w-4",
  lg: "h-5 w-5",
};

export function RatingStars({
  value,
  onChange,
  size = "default",
  showValue = false,
  className,
}: RatingStarsProps) {
  const isInteractive = typeof onChange === "function";
  const [hovered, setHovered] = React.useState<number | null>(null);
  const displayValue = hovered ?? value;
  const starClass = SIZE_MAP[size];

  return (
    <div
      className={cn("inline-flex items-center gap-0.5", className)}
      role={isInteractive ? "radiogroup" : "img"}
      aria-label={isInteractive ? "Rate this" : `Rated ${value} out of 5 stars`}
    >
      {[1, 2, 3, 4, 5].map((starIndex) => {
        const fillFraction = Math.max(0, Math.min(1, displayValue - (starIndex - 1)));

        const star = (
          <span key={starIndex} className="relative inline-block">
            <Star className={cn(starClass, "text-muted-foreground/30")} aria-hidden="true" />
            {fillFraction > 0 && (
              <span
                className="absolute inset-0 overflow-hidden"
                style={{ width: `${fillFraction * 100}%` }}
              >
                <Star className={cn(starClass, "fill-warning text-warning")} aria-hidden="true" />
              </span>
            )}
          </span>
        );

        if (!isInteractive) return star;

        return (
          <button
            key={starIndex}
            type="button"
            role="radio"
            aria-checked={value === starIndex}
            aria-label={`${starIndex} star${starIndex > 1 ? "s" : ""}`}
            onMouseEnter={() => setHovered(starIndex)}
            onMouseLeave={() => setHovered(null)}
            onClick={() => onChange(starIndex)}
            className="rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1"
          >
            {star}
          </button>
        );
      })}
      {showValue && (
        <span className="ml-1 text-sm font-medium text-foreground">{value.toFixed(1)}</span>
      )}
    </div>
  );
}

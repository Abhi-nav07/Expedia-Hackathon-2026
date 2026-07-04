import type { LucideIcon } from "lucide-react";
import { Check, Circle } from "lucide-react";

import { cn } from "@/lib/utils/cn";

export type TimelineStatus = "completed" | "current" | "upcoming";

export interface TimelineEvent {
  id: string;
  title: string;
  description?: string;
  timestamp?: string;
  icon?: LucideIcon;
  status: TimelineStatus;
}

export interface TripTimelineProps {
  events: TimelineEvent[];
  className?: string;
}

/**
 * Generic vertical timeline — no assumption about what an "event" is
 * (flight leg, hotel check-in, activity, approval step, etc.), so it's
 * reusable for trip itineraries, booking status, or any future
 * multi-stage flow the challenge introduces.
 */
export function TripTimeline({ events, className }: TripTimelineProps) {
  return (
    <ol className={cn("relative", className)}>
      {events.map((event, index) => {
        const Icon = event.icon;
        const isLast = index === events.length - 1;

        return (
          <li key={event.id} className="relative flex gap-4 pb-8 last:pb-0">
            {!isLast && (
              <span
                className={cn(
                  "absolute left-[15px] top-8 h-[calc(100%-1rem)] w-px",
                  event.status === "completed" ? "bg-primary" : "bg-border"
                )}
                aria-hidden="true"
              />
            )}

            <span
              className={cn(
                "relative flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2",
                event.status === "completed" && "border-primary bg-primary text-primary-foreground",
                event.status === "current" && "border-primary bg-background text-primary",
                event.status === "upcoming" && "border-border bg-background text-muted-foreground"
              )}
            >
              {event.status === "completed" ? (
                <Check className="h-4 w-4" />
              ) : Icon ? (
                <Icon className="h-4 w-4" />
              ) : (
                <Circle className="h-2 w-2 fill-current" />
              )}
            </span>

            <div className="flex-1 pt-1">
              <div className="flex items-baseline justify-between gap-2">
                <p
                  className={cn(
                    "text-sm font-medium",
                    event.status === "upcoming" && "text-muted-foreground"
                  )}
                >
                  {event.title}
                </p>
                {event.timestamp && (
                  <time className="shrink-0 text-xs text-muted-foreground">{event.timestamp}</time>
                )}
              </div>
              {event.description && (
                <p className="mt-0.5 text-sm text-muted-foreground">{event.description}</p>
              )}
            </div>
          </li>
        );
      })}
    </ol>
  );
}

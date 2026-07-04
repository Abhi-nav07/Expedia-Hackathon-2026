import { Plane } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils/cn";

export interface FlightSegment {
  airline: string;
  flightNumber: string;
  departureTime: string; // ISO string — formatting is the caller's concern
  departureAirport: string;
  arrivalTime: string;
  arrivalAirport: string;
  durationMinutes: number;
  stops: number;
}

export interface FlightCardProps {
  id: string;
  segment: FlightSegment;
  price: number;
  currency?: string;
  onSelect?: (id: string) => void;
  className?: string;
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" });
}

function formatDuration(minutes: number): string {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return `${h}h ${m > 0 ? `${m}m` : ""}`.trim();
}

/** UI-only flight card — no fare rules, seat inventory, or search-ranking logic. */
export function FlightCard({ id, segment, price, currency = "USD", onSelect, className }: FlightCardProps) {
  const {
    airline,
    flightNumber,
    departureTime,
    departureAirport,
    arrivalTime,
    arrivalAirport,
    durationMinutes,
    stops,
  } = segment;

  return (
    <Card className={cn("p-4", className)}>
      <CardContent className="flex flex-col gap-4 p-0 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-muted">
            <Plane className="h-5 w-5 text-muted-foreground" aria-hidden="true" />
          </div>
          <div>
            <p className="text-sm font-medium">
              {airline} · {flightNumber}
            </p>
            <p className="text-xs text-muted-foreground">{formatDuration(durationMinutes)}</p>
          </div>
        </div>

        <div className="flex flex-1 items-center justify-center gap-3 sm:justify-start">
          <div className="text-center">
            <p className="font-semibold">{formatTime(departureTime)}</p>
            <p className="text-xs text-muted-foreground">{departureAirport}</p>
          </div>
          <div className="flex flex-col items-center gap-1 px-2">
            <div className="h-px w-12 bg-border" />
            <Badge variant={stops === 0 ? "success" : "secondary"} className="text-[10px]">
              {stops === 0 ? "Nonstop" : `${stops} stop${stops > 1 ? "s" : ""}`}
            </Badge>
          </div>
          <div className="text-center">
            <p className="font-semibold">{formatTime(arrivalTime)}</p>
            <p className="text-xs text-muted-foreground">{arrivalAirport}</p>
          </div>
        </div>

        <div className="flex items-center justify-between gap-4 sm:flex-col sm:items-end sm:gap-1">
          <span className="text-lg font-semibold">
            {new Intl.NumberFormat("en-US", { style: "currency", currency }).format(price)}
          </span>
          <Button size="sm" onClick={() => onSelect?.(id)}>
            Select
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

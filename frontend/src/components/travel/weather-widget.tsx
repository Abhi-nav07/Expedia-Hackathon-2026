import { Cloud, CloudRain, CloudSnow, Sun, CloudDrizzle, Zap, type LucideIcon } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils/cn";

export type WeatherCondition = "sunny" | "cloudy" | "rainy" | "drizzle" | "snowy" | "stormy";

export interface WeatherWidgetProps {
  location: string;
  condition: WeatherCondition;
  temperature: number;
  /** "C" or "F" — purely a display label, no conversion performed. */
  unit?: "C" | "F";
  high?: number;
  low?: number;
  className?: string;
}

const CONDITION_ICON: Record<WeatherCondition, LucideIcon> = {
  sunny: Sun,
  cloudy: Cloud,
  rainy: CloudRain,
  drizzle: CloudDrizzle,
  snowy: CloudSnow,
  stormy: Zap,
};

const CONDITION_LABEL: Record<WeatherCondition, string> = {
  sunny: "Sunny",
  cloudy: "Cloudy",
  rainy: "Rainy",
  drizzle: "Drizzle",
  snowy: "Snowy",
  stormy: "Stormy",
};

/**
 * Purely presentational — no weather API is wired up (no provider or
 * key configured in this platform yet). Pass real data in via props
 * once a weather module/integration exists.
 */
export function WeatherWidget({
  location,
  condition,
  temperature,
  unit = "F",
  high,
  low,
  className,
}: WeatherWidgetProps) {
  const Icon = CONDITION_ICON[condition];

  return (
    <Card className={cn("p-4", className)}>
      <CardContent className="flex items-center justify-between p-0">
        <div>
          <p className="text-sm font-medium text-muted-foreground">{location}</p>
          <p className="text-3xl font-semibold">
            {Math.round(temperature)}°{unit}
          </p>
          <p className="text-sm text-muted-foreground">{CONDITION_LABEL[condition]}</p>
          {(high !== undefined || low !== undefined) && (
            <p className="mt-1 text-xs text-muted-foreground">
              {high !== undefined && `H: ${Math.round(high)}°`}
              {high !== undefined && low !== undefined && "  "}
              {low !== undefined && `L: ${Math.round(low)}°`}
            </p>
          )}
        </div>
        <Icon className="h-12 w-12 text-primary" aria-hidden="true" />
      </CardContent>
    </Card>
  );
}

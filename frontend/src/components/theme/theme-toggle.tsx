"use client";

import { Laptop, Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

import { cn } from "@/lib/utils/cn";

const THEME_CYCLE = ["light", "dark", "system"] as const;
type ThemeOption = (typeof THEME_CYCLE)[number];

const THEME_ICONS: Record<ThemeOption, typeof Sun> = {
  light: Sun,
  dark: Moon,
  system: Laptop,
};

const THEME_LABELS: Record<ThemeOption, string> = {
  light: "Light mode",
  dark: "Dark mode",
  system: "System theme",
};

export function ThemeToggle({ className }: { className?: string }) {
  const { theme, setTheme } = useTheme();
  // Avoid hydration mismatch: next-themes can't know the persisted
  // preference until mounted client-side, so render a neutral state
  // until then rather than guessing.
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const current = (theme as ThemeOption) ?? "system";
  const Icon = mounted ? THEME_ICONS[current] : Laptop;

  const cycleTheme = () => {
    const currentIndex = THEME_CYCLE.indexOf(current);
    const next = THEME_CYCLE[(currentIndex + 1) % THEME_CYCLE.length] ?? "system";
    setTheme(next);
  };

  return (
    <button
      type="button"
      onClick={cycleTheme}
      aria-label={mounted ? `Switch theme (current: ${THEME_LABELS[current]})` : "Switch theme"}
      title={mounted ? THEME_LABELS[current] : undefined}
      className={cn(
        "inline-flex h-9 w-9 items-center justify-center rounded-md",
        "text-foreground/70 transition-colors hover:bg-accent hover:text-foreground",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
        className
      )}
    >
      <Icon className="h-[1.15rem] w-[1.15rem]" aria-hidden="true" />
    </button>
  );
}

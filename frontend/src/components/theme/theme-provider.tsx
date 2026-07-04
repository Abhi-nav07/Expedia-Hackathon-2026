"use client";

import { ThemeProvider as NextThemesProvider } from "next-themes";
import type { ThemeProviderProps } from "next-themes/dist/types";

/**
 * Thin wrapper around next-themes so the rest of the app imports from
 * our own components/ tree rather than the library directly — if we
 * ever swap the underlying implementation, only this file changes.
 *
 * attribute="class" toggles the `dark` class on <html>, which is what
 * globals.css's `.dark { ... }` block (see Module 05) and every
 * Tailwind `dark:` variant key off. defaultTheme="system" respects the
 * user's OS preference on first visit; the choice is then persisted to
 * localStorage by next-themes — this is a UI preference, not sensitive
 * data, so localStorage is the right (and only sane) place for it,
 * unlike the auth token in store/auth-store.ts.
 */
export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
      {...props}
    >
      {children}
    </NextThemesProvider>
  );
}

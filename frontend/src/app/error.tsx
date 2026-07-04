"use client";

import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // In a real deployment this reports to an error-tracking service
    // (Sentry, etc.) rather than console — wiring that is a DevOps-module
    // concern. Never render error.message directly to the user: it may
    // contain details we don't want surfaced (matches backend's approach
    // in core/exceptions.py of never leaking internals).
    console.error("Unhandled client error", { digest: error.digest });
  }, [error]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-8 text-center">
      <h1 className="text-2xl font-semibold">Something went wrong</h1>
      <p className="text-muted-foreground">
        An unexpected error occurred. Please try again.
      </p>
      <button
        onClick={reset}
        className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
      >
        Try again
      </button>
    </main>
  );
}

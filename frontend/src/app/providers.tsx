"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState, useEffect, type ReactNode } from "react";

import { ThemeProvider } from "@/components/theme/theme-provider";
import { bootstrapAuth } from "@/lib/api/client";

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Sensible hackathon-scale defaults: avoid refetch storms,
            // but don't cache so aggressively that demo data goes stale.
            staleTime: 30_000,
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  useEffect(() => {
    // Silently attempt to restore a session on page load using the
    // httpOnly refresh cookie, so a reload doesn't force a re-login.
    void bootstrapAuth();
  }, []);

  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </ThemeProvider>
  );
}

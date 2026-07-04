"use client";

import { useTheme } from "next-themes";
import type * as React from "react";
import { Toaster as SonnerToaster, toast } from "sonner";

type ToasterProps = React.ComponentProps<typeof SonnerToaster>;

/**
 * Mount <Toaster /> once, near the root (see app/providers.tsx). Then
 * call the exported `toast(...)` function from anywhere in the app —
 * no context/provider prop-drilling needed, sonner manages its own
 * portal and queue.
 *
 * Usage: toast.success("Booking confirmed"), toast.error("Something went wrong"),
 * toast("Plain message"), toast.promise(apiCall(), { loading, success, error }).
 */
function Toaster({ ...props }: ToasterProps) {
  const { theme = "system" } = useTheme();

  return (
    <SonnerToaster
      theme={theme as ToasterProps["theme"]}
      className="toaster group"
      toastOptions={{
        classNames: {
          toast:
            "group toast group-[.toaster]:bg-card group-[.toaster]:text-card-foreground " +
            "group-[.toaster]:border-border group-[.toaster]:shadow-lg",
          description: "group-[.toast]:text-muted-foreground",
          actionButton: "group-[.toast]:bg-primary group-[.toast]:text-primary-foreground",
          cancelButton: "group-[.toast]:bg-muted group-[.toast]:text-muted-foreground",
          success: "group-[.toaster]:!text-success",
          error: "group-[.toaster]:!text-destructive",
          warning: "group-[.toaster]:!text-warning",
        },
      }}
      {...props}
    />
  );
}

export { Toaster, toast };

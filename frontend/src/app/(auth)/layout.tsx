import Link from "next/link";
import type { ReactNode } from "react";

/**
 * Layout for the (auth) route group — applies to login, register,
 * forgot-password, reset-password, verify-email. Route group
 * parentheses don't appear in the URL (Next.js convention); they just
 * group these pages under a shared, minimal chrome distinct from the
 * (dashboard) group's Sidebar+Navbar shell.
 */
export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-muted/30 p-4">
      <Link href="/" className="mb-8 text-lg font-semibold">
        Expedia Hackathon
      </Link>
      <div className="w-full max-w-md">{children}</div>
    </div>
  );
}

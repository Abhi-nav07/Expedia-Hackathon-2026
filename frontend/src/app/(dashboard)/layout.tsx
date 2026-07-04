import type { ReactNode } from "react";

import { Navbar } from "@/components/layout/navbar";
import { Sidebar } from "@/components/layout/sidebar";

/**
 * Layout for the (dashboard) route group — applies to every page placed
 * under app/(dashboard)/, e.g. dashboard/, analytics/, admin/,
 * settings/, bookings/, wishlist/, profile/, notifications/. Route
 * group parentheses are a Next.js convention: they don't appear in the
 * URL, just group pages under a shared layout.
 *
 * Actual page content (Dashboard, Analytics, etc.) is Frontend Pages
 * module territory — this only provides the persistent chrome around
 * whatever page is rendered.
 */
export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Navbar />
        <main className="flex-1 overflow-y-auto p-4 md:p-6">{children}</main>
      </div>
    </div>
  );
}

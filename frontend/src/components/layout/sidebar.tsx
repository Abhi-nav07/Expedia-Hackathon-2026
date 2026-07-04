"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { getVisibleNavItems } from "@/lib/constants/nav";
import { cn } from "@/lib/utils/cn";
import { useAuthStore } from "@/store/auth-store";

export function Sidebar({ className }: { className?: string }) {
  const pathname = usePathname();
  const role = useAuthStore((state) => state.user?.role);
  const items = getVisibleNavItems(role);

  return (
    <aside
      className={cn(
        "hidden w-60 shrink-0 flex-col border-r border-border bg-card md:flex",
        className
      )}
    >
      <div className="flex h-16 items-center px-6">
        <Link href="/dashboard" className="text-base font-semibold">
          Expedia Hackathon
        </Link>
      </div>
      <nav className="flex-1 space-y-1 px-3 py-2">
        {items.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              aria-current={isActive ? "page" : undefined}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors duration-fast",
                isActive
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground hover:bg-accent/50 hover:text-foreground"
              )}
            >
              <Icon className="h-4 w-4 shrink-0" aria-hidden="true" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}

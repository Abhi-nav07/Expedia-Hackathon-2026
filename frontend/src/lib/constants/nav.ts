import type { LucideIcon } from "lucide-react";
import {
  LayoutDashboard,
  BarChart3,
  Search,
  Map,
  Compass,
  Heart,
  CalendarClock,
  Bell,
  Settings,
  ShieldCheck,
} from "lucide-react";

import type { UserRole } from "@/types/user";

export interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  /** Restrict visibility to specific roles. Omit to show to every authenticated user. */
  roles?: UserRole[];
}

/**
 * Single source of truth for primary navigation. Sidebar (desktop) and
 * the mobile nav Sheet both render from this list, so adding a page
 * later only requires one edit here — not two components kept in sync
 * by hand.
 */
export const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Analytics", href: "/analytics", icon: BarChart3 },
  { label: "Explore", href: "/explore", icon: Compass },
  { label: "Search", href: "/search", icon: Search },
  { label: "Maps", href: "/maps", icon: Map },
  { label: "Wishlist", href: "/wishlist", icon: Heart },
  { label: "Bookings", href: "/bookings", icon: CalendarClock },
  { label: "Notifications", href: "/notifications", icon: Bell },
  { label: "Settings", href: "/settings", icon: Settings },
  { label: "Admin", href: "/admin", icon: ShieldCheck, roles: ["admin"] },
];

export function getVisibleNavItems(role: UserRole | undefined): NavItem[] {
  return NAV_ITEMS.filter((item) => !item.roles || (role && item.roles.includes(role)));
}

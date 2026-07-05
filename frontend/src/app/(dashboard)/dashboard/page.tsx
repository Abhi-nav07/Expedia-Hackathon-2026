"use client";

import { Activity, CheckCircle2, Settings, ShieldCheck, User as UserIcon } from "lucide-react";
import Link from "next/link";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { useCurrentUser } from "@/hooks/use-auth";
import { resolveAvatarUrl } from "@/lib/utils/backend-origin";
import { getInitialsFromName } from "@/lib/utils/initials";

function StatCard({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Activity;
  label: string;
  value: string;
}) {
  return (
    <Card>
      <CardContent className="flex items-center gap-4 p-6">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10">
          <Icon className="h-5 w-5 text-primary" aria-hidden="true" />
        </div>
        <div>
          <p className="text-sm text-muted-foreground">{label}</p>
          <p className="text-lg font-semibold">{value}</p>
        </div>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const { data: user, isLoading } = useCurrentUser();

  return (
    <div className="space-y-6">
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href="/dashboard">Home</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>Dashboard</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          {isLoading ? (
            <Skeleton className="h-8 w-64" />
          ) : (
            <h1 className="text-2xl font-semibold">
              Welcome back{user?.full_name ? `, ${user.full_name.split(" ")[0]}` : ""}
            </h1>
          )}
          <p className="mt-1 text-sm text-muted-foreground">
            Here&apos;s what&apos;s happening with your account.
          </p>
        </div>
        <Link href="/profile">
          <Button variant="outline">View profile</Button>
        </Link>
      </div>

      {/* Stat cards — real account facts, not fabricated business metrics
          (no bookings/business logic exists yet — see Module 11 notes) */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard
          icon={ShieldCheck}
          label="Account status"
          value={user?.is_active ? "Active" : "Inactive"}
        />
        <StatCard
          icon={CheckCircle2}
          label="Email verification"
          value={user?.is_email_verified ? "Verified" : "Unverified"}
        />
        <StatCard icon={UserIcon} label="Role" value={user?.role ?? "—"} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-base">Profile summary</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading || !user ? (
              <div className="space-y-3">
                <Skeleton className="h-12 w-12 rounded-full" />
                <Skeleton className="h-4 w-32" />
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Avatar className="h-12 w-12">
                  <AvatarImage src={resolveAvatarUrl(user.avatar_url)} alt={user.full_name} />
                  <AvatarFallback>{getInitialsFromName(user.full_name)}</AvatarFallback>
                </Avatar>
                <div>
                  <p className="font-medium">{user.full_name}</p>
                  <p className="text-sm text-muted-foreground">{user.email}</p>
                  <Badge variant="secondary" className="mt-1 capitalize">
                    {user.role}
                  </Badge>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-base">Quick actions</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-2">
            <Link href="/profile">
              <Button variant="outline" className="w-full justify-start gap-2">
                <UserIcon className="h-4 w-4" />
                Edit profile
              </Button>
            </Link>
            <Link href="/profile">
              <Button variant="outline" className="w-full justify-start gap-2">
                <Settings className="h-4 w-4" />
                Preferences
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Recent activity — honest placeholder, no fabricated data */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-base">Recent activity</CardTitle>
          </CardHeader>
          <CardContent>
            <EmptyState
              icon={Activity}
              title="No recent activity"
              description="Activity will appear here once the platform has features that generate it."
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

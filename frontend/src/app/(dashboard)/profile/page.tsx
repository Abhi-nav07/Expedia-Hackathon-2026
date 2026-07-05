"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2 } from "lucide-react";
import * as React from "react";
import { useForm } from "react-hook-form";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useCurrentUser, useResendVerification } from "@/hooks/use-auth";
import {
  usePreferences,
  useUpdatePreferences,
  useUpdateProfile,
  useUploadAvatar,
} from "@/hooks/use-profile";
import { resolveAvatarUrl } from "@/lib/utils/backend-origin";
import { getInitialsFromName } from "@/lib/utils/initials";
import { type ProfileUpdateFormValues, profileUpdateSchema } from "@/lib/validators/auth";

function AccountTab() {
  const { data: user, isLoading } = useCurrentUser();
  const updateProfile = useUpdateProfile();
  const uploadAvatar = useUploadAvatar();
  const resendVerification = useResendVerification();
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm<ProfileUpdateFormValues>({
    resolver: zodResolver(profileUpdateSchema),
    values: user ? { full_name: user.full_name } : undefined,
  });

  const onSubmit = (values: ProfileUpdateFormValues) => {
    updateProfile.mutate(values, { onSuccess: () => reset(values) });
  };

  const handleAvatarClick = () => fileInputRef.current?.click();

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) uploadAvatar.mutate(file);
    e.target.value = ""; // allow re-selecting the same file later
  };

  if (isLoading || !user) {
    return (
      <Card>
        <CardContent className="space-y-4 p-6">
          <Skeleton className="h-16 w-16 rounded-full" />
          <Skeleton className="h-4 w-48" />
          <Skeleton className="h-4 w-32" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Account information</CardTitle>
        <CardDescription>Your profile details and avatar.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-center gap-4">
          <button
            type="button"
            onClick={handleAvatarClick}
            className="group relative rounded-full focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            aria-label="Change avatar"
          >
            <Avatar className="h-16 w-16">
              <AvatarImage src={resolveAvatarUrl(user.avatar_url)} alt={user.full_name} />
              <AvatarFallback className="text-lg">
                {getInitialsFromName(user.full_name)}
              </AvatarFallback>
            </Avatar>
            <div className="absolute inset-0 flex items-center justify-center rounded-full bg-black/40 text-xs font-medium text-white opacity-0 transition-opacity group-hover:opacity-100">
              {uploadAvatar.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Change"}
            </div>
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
            onChange={handleAvatarChange}
          />
          <div>
            <p className="font-medium">{user.full_name}</p>
            <p className="text-sm text-muted-foreground">{user.email}</p>
            <div className="mt-1 flex gap-1.5">
              <Badge variant="secondary" className="capitalize">
                {user.role}
              </Badge>
              <Badge variant={user.is_email_verified ? "success" : "warning"}>
                {user.is_email_verified ? "Verified" : "Unverified"}
              </Badge>
            </div>
          </div>
        </div>

        {!user.is_email_verified && (
          <div className="flex items-center justify-between rounded-md border border-warning/50 bg-warning/10 p-3 text-sm">
            <span>Your email address isn&apos;t verified yet.</span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => resendVerification.mutate()}
              isLoading={resendVerification.isPending}
            >
              Resend link
            </Button>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
          <div className="space-y-2">
            <Label htmlFor="full_name">Full name</Label>
            <Input id="full_name" invalid={!!errors.full_name} {...register("full_name")} />
            {errors.full_name && (
              <p className="text-sm text-destructive">{errors.full_name.message}</p>
            )}
          </div>
          <div className="space-y-2">
            <Label>Email</Label>
            <Input value={user.email} disabled />
            <p className="text-xs text-muted-foreground">
              Email changes aren&apos;t supported yet.
            </p>
          </div>
        </form>
      </CardContent>
      <CardFooter>
        <Button
          onClick={handleSubmit(onSubmit)}
          disabled={!isDirty}
          isLoading={updateProfile.isPending}
        >
          Save changes
        </Button>
      </CardFooter>
    </Card>
  );
}

function PreferencesTab() {
  const { data, isLoading } = usePreferences();
  const updatePreferences = useUpdatePreferences();

  const [theme, setTheme] = React.useState<string>("system");
  const [currency, setCurrency] = React.useState<string>("");
  const [language, setLanguage] = React.useState<string>("");
  const [notifications, setNotifications] = React.useState<boolean>(true);

  React.useEffect(() => {
    if (data) {
      setTheme((data.preferences.theme as string) ?? "system");
      setCurrency((data.preferences.currency as string) ?? "");
      setLanguage((data.preferences.language as string) ?? "");
      setNotifications(Boolean(data.preferences.notifications_enabled ?? true));
    }
  }, [data]);

  if (isLoading) {
    return (
      <Card>
        <CardContent className="space-y-4 p-6">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
        </CardContent>
      </Card>
    );
  }

  const handleSave = () => {
    updatePreferences.mutate({
      theme: theme as "light" | "dark" | "system",
      currency: currency || undefined,
      language: language || undefined,
      notifications_enabled: notifications,
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Preferences</CardTitle>
        <CardDescription>
          Stored on your account — separate from the theme toggle in the navbar, which changes
          what you see right now.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label>Preferred theme</Label>
          <Select value={theme} onValueChange={setTheme}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="light">Light</SelectItem>
              <SelectItem value="dark">Dark</SelectItem>
              <SelectItem value="system">System</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="currency">Currency</Label>
            <Input
              id="currency"
              placeholder="USD"
              maxLength={3}
              value={currency}
              onChange={(e) => setCurrency(e.target.value.toUpperCase())}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="language">Language</Label>
            <Input
              id="language"
              placeholder="en"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            />
          </div>
        </div>

        <div className="flex items-center justify-between rounded-md border border-border p-3">
          <div>
            <p className="text-sm font-medium">Notifications</p>
            <p className="text-xs text-muted-foreground">
              Receive account-related notifications.
            </p>
          </div>
          <Switch checked={notifications} onCheckedChange={setNotifications} />
        </div>
      </CardContent>
      <CardFooter>
        <Button onClick={handleSave} isLoading={updatePreferences.isPending}>
          Save preferences
        </Button>
      </CardFooter>
    </Card>
  );
}

export default function ProfilePage() {
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Profile</h1>
        <p className="text-sm text-muted-foreground">Manage your account and preferences.</p>
      </div>

      <Tabs defaultValue="account">
        <TabsList>
          <TabsTrigger value="account">Account</TabsTrigger>
          <TabsTrigger value="preferences">Preferences</TabsTrigger>
        </TabsList>
        <TabsContent value="account">
          <AccountTab />
        </TabsContent>
        <TabsContent value="preferences">
          <PreferencesTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}

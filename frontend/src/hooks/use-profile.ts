"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { toast } from "@/components/ui/toaster";
import { ApiError } from "@/lib/api/client";
import { type PreferencesPayload, type UpdateProfilePayload, usersApi } from "@/lib/api/users";
import { CURRENT_USER_QUERY_KEY } from "@/hooks/use-auth";

const PREFERENCES_QUERY_KEY = ["preferences"] as const;

function errorMessage(err: unknown, fallback: string): string {
  return err instanceof ApiError ? err.message : fallback;
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: UpdateProfilePayload) => usersApi.updateProfile(payload),
    onSuccess: (updatedUser) => {
      queryClient.setQueryData(CURRENT_USER_QUERY_KEY, updatedUser);
      toast.success("Profile updated");
    },
    onError: (err) => {
      toast.error(errorMessage(err, "Couldn't update your profile. Please try again."));
    },
  });
}

export function usePreferences() {
  return useQuery({
    queryKey: PREFERENCES_QUERY_KEY,
    queryFn: usersApi.getPreferences,
    staleTime: 60_000,
  });
}

export function useUpdatePreferences() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: PreferencesPayload) => usersApi.updatePreferences(payload),
    onSuccess: (data) => {
      queryClient.setQueryData(PREFERENCES_QUERY_KEY, data);
      toast.success("Preferences saved");
    },
    onError: (err) => {
      toast.error(errorMessage(err, "Couldn't save your preferences. Please try again."));
    },
  });
}

export function useUploadAvatar() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => usersApi.uploadAvatar(file),
    onSuccess: () => {
      // Re-fetch the full user rather than patching avatar_url locally —
      // simpler and guarantees the displayed avatar always matches
      // exactly what the server persisted.
      queryClient.invalidateQueries({ queryKey: CURRENT_USER_QUERY_KEY });
      toast.success("Avatar updated");
    },
    onError: (err) => {
      toast.error(errorMessage(err, "Couldn't upload that image. Please try a different file."));
    },
  });
}

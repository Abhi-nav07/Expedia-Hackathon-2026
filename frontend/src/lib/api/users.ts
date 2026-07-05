import { apiClient } from "@/lib/api/client";
import type { User } from "@/types/user";

export interface UpdateProfilePayload {
  full_name?: string;
}

export interface PreferencesPayload {
  theme?: "light" | "dark" | "system";
  language?: string;
  currency?: string;
  notifications_enabled?: boolean;
}

export interface PreferencesResponse {
  preferences: Record<string, unknown>;
}

export interface AvatarUploadResponse {
  avatar_url: string;
}

export const usersApi = {
  updateProfile: (payload: UpdateProfilePayload) =>
    apiClient.patch<User>("/users/me", payload),

  getPreferences: () => apiClient.get<PreferencesResponse>("/users/me/preferences"),

  updatePreferences: (payload: PreferencesPayload) =>
    apiClient.put<PreferencesResponse>("/users/me/preferences", payload),

  uploadAvatar: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient.upload<AvatarUploadResponse>("/users/me/avatar", formData);
  },
};

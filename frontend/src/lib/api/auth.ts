import { apiClient } from "@/lib/api/client";
import type { TokenResponse, User } from "@/types/user";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
}

export const authApi = {
  login: (payload: LoginPayload) =>
    apiClient.post<TokenResponse>("/auth/login", payload),

  register: (payload: RegisterPayload) =>
    apiClient.post<User>("/auth/register", payload),

  me: () => apiClient.get<User>("/auth/me"),

  logout: () => apiClient.post<void>("/auth/logout"),
};

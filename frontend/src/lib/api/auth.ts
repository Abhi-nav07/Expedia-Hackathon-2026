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

export interface ChangePasswordPayload {
  current_password: string;
  new_password: string;
}

export interface ForgotPasswordPayload {
  email: string;
}

export interface ResetPasswordPayload {
  token: string;
  new_password: string;
}

export interface VerifyEmailPayload {
  token: string;
}

export const authApi = {
  login: (payload: LoginPayload) =>
    apiClient.post<TokenResponse>("/auth/login", payload),

  register: (payload: RegisterPayload) =>
    apiClient.post<User>("/auth/register", payload),

  me: () => apiClient.get<User>("/auth/me"),

  logout: () => apiClient.post<void>("/auth/logout"),

  changePassword: (payload: ChangePasswordPayload) =>
    apiClient.post<void>("/auth/change-password", payload),

  forgotPassword: (payload: ForgotPasswordPayload) =>
    apiClient.post<{ message: string }>("/auth/forgot-password", payload),

  resetPassword: (payload: ResetPasswordPayload) =>
    apiClient.post<void>("/auth/reset-password", payload),

  resendVerification: () =>
    apiClient.post<{ message: string }>("/auth/resend-verification"),

  verifyEmail: (payload: VerifyEmailPayload) =>
    apiClient.post<void>("/auth/verify-email", payload),
};

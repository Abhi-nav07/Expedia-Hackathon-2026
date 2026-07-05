"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";

import { toast } from "@/components/ui/toaster";
import {
  authApi,
  type ForgotPasswordPayload,
  type LoginPayload,
  type RegisterPayload,
  type ResetPasswordPayload,
  type VerifyEmailPayload,
} from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";
import { useAuthStore } from "@/store/auth-store";

export const CURRENT_USER_QUERY_KEY = ["currentUser"] as const;

function errorMessage(err: unknown, fallback: string): string {
  return err instanceof ApiError ? err.message : fallback;
}

/**
 * Live current-user query. Seeded with the auth store's snapshot (set
 * immediately on login/refresh) via `initialData` for instant paint,
 * then revalidates against /auth/me in the background — so profile
 * edits made in another tab, or role changes, eventually reflect here
 * without a manual page reload.
 */
export function useCurrentUser() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const storeUser = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: CURRENT_USER_QUERY_KEY,
    queryFn: authApi.me,
    enabled: isAuthenticated,
    initialData: storeUser ?? undefined,
    staleTime: 60_000,
  });
}

export function useLogin() {
  const setAuth = useAuthStore((state) => state.setAuth);
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: (payload: LoginPayload) => authApi.login(payload),
    onSuccess: (data) => {
      setAuth(data.access_token, data.user);
      queryClient.setQueryData(CURRENT_USER_QUERY_KEY, data.user);
      toast.success("Welcome back!");
      router.push("/dashboard");
    },
    onError: (err) => {
      toast.error(errorMessage(err, "Login failed. Please check your credentials."));
    },
  });
}

export function useRegister() {
  const router = useRouter();

  return useMutation({
    mutationFn: (payload: RegisterPayload) => authApi.register(payload),
    onSuccess: () => {
      // Registration deliberately does NOT log the user in (matches
      // backend/app/api/v1/routers/auth.py's documented behavior) — send
      // them to login rather than pretending they have a session.
      toast.success("Account created. Please log in.");
      router.push("/login");
    },
    onError: (err) => {
      toast.error(errorMessage(err, "Registration failed. Please try again."));
    },
  });
}

export function useLogout() {
  const clearAuth = useAuthStore((state) => state.clearAuth);
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: () => authApi.logout(),
    onSettled: () => {
      // Logout is best-effort server-side (see backend auth router's
      // comment on token revocation) — clear local state regardless of
      // whether the API call itself succeeded. A network hiccup should
      // never prevent someone from signing out locally.
      clearAuth();
      queryClient.removeQueries({ queryKey: CURRENT_USER_QUERY_KEY });
      toast.success("Signed out");
      router.push("/login");
    },
  });
}

export function useForgotPassword() {
  return useMutation({
    mutationFn: (payload: ForgotPasswordPayload) => authApi.forgotPassword(payload),
    onSuccess: () => {
      // Always shows the same message regardless of whether the email
      // exists — matches the backend's anti-enumeration design (always
      // 202). Never branch this message on the response content.
      toast.success("If an account with that email exists, a reset link has been sent.");
    },
    onError: (err) => {
      toast.error(errorMessage(err, "Something went wrong. Please try again."));
    },
  });
}

export function useResetPassword() {
  const router = useRouter();

  return useMutation({
    mutationFn: (payload: ResetPasswordPayload) => authApi.resetPassword(payload),
    onSuccess: () => {
      toast.success("Password reset. Please log in with your new password.");
      router.push("/login");
    },
    onError: (err) => {
      toast.error(errorMessage(err, "Invalid or expired reset link."));
    },
  });
}

export function useVerifyEmail() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: VerifyEmailPayload) => authApi.verifyEmail(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CURRENT_USER_QUERY_KEY });
    },
  });
}

export function useResendVerification() {
  return useMutation({
    mutationFn: () => authApi.resendVerification(),
    onSuccess: () => {
      toast.success("Verification email sent — check your inbox.");
    },
    onError: (err) => {
      toast.error(errorMessage(err, "Couldn't resend the verification email."));
    },
  });
}

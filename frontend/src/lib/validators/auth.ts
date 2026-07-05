import { z } from "zod";

/**
 * Mirrors backend/app/schemas/auth.py's validate_password_complexity
 * exactly (min 10 chars, needs uppercase/lowercase/digit) — giving
 * immediate client-side feedback that matches what the server will
 * actually accept or reject, rather than a generic "8 characters"
 * placeholder rule that silently mismatches the API.
 */
const passwordComplexitySchema = z
  .string()
  .min(10, "Must be at least 10 characters")
  .max(128, "Must be at most 128 characters")
  .regex(/[A-Z]/, "Must contain at least one uppercase letter")
  .regex(/[a-z]/, "Must contain at least one lowercase letter")
  .regex(/\d/, "Must contain at least one digit");

export const loginSchema = z.object({
  email: z.string().min(1, "Email is required").email("Enter a valid email address"),
  password: z.string().min(1, "Password is required"),
});
export type LoginFormValues = z.infer<typeof loginSchema>;

export const registerSchema = z.object({
  full_name: z.string().min(1, "Full name is required").max(255),
  email: z.string().min(1, "Email is required").email("Enter a valid email address"),
  password: passwordComplexitySchema,
});
export type RegisterFormValues = z.infer<typeof registerSchema>;

export const forgotPasswordSchema = z.object({
  email: z.string().min(1, "Email is required").email("Enter a valid email address"),
});
export type ForgotPasswordFormValues = z.infer<typeof forgotPasswordSchema>;

export const resetPasswordSchema = z.object({
  new_password: passwordComplexitySchema,
});
export type ResetPasswordFormValues = z.infer<typeof resetPasswordSchema>;

export const changePasswordSchema = z.object({
  current_password: z.string().min(1, "Current password is required"),
  new_password: passwordComplexitySchema,
});
export type ChangePasswordFormValues = z.infer<typeof changePasswordSchema>;

export const profileUpdateSchema = z.object({
  full_name: z.string().min(1, "Full name is required").max(255),
});
export type ProfileUpdateFormValues = z.infer<typeof profileUpdateSchema>;

export const preferencesSchema = z.object({
  theme: z.enum(["light", "dark", "system"]).optional(),
  language: z.string().min(2).max(10).optional().or(z.literal("")),
  currency: z.string().length(3, "Use a 3-letter currency code, e.g. USD").optional().or(z.literal("")),
  notifications_enabled: z.boolean().optional(),
});
export type PreferencesFormValues = z.infer<typeof preferencesSchema>;

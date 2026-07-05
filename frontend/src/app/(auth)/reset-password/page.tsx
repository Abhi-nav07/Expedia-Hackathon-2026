"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { PasswordInput } from "@/components/forms/password-input";
import { useResetPassword } from "@/hooks/use-auth";
import { type ResetPasswordFormValues, resetPasswordSchema } from "@/lib/validators/auth";

function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const resetPassword = useResetPassword();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetPasswordFormValues>({ resolver: zodResolver(resetPasswordSchema) });

  if (!token) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Invalid reset link</CardTitle>
          <CardDescription>
            This link is missing its reset token. Request a new one below.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Link href="/forgot-password">
            <Button className="w-full">Request a new link</Button>
          </Link>
        </CardContent>
      </Card>
    );
  }

  const onSubmit = (values: ResetPasswordFormValues) =>
    resetPassword.mutate({ token, new_password: values.new_password });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Reset your password</CardTitle>
        <CardDescription>Choose a new password for your account.</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
          <div className="space-y-2">
            <Label htmlFor="new_password">New password</Label>
            <PasswordInput
              id="new_password"
              autoComplete="new-password"
              invalid={!!errors.new_password}
              {...register("new_password")}
            />
            {errors.new_password ? (
              <p className="text-sm text-destructive">{errors.new_password.message}</p>
            ) : (
              <p className="text-xs text-muted-foreground">
                At least 10 characters, with an uppercase letter, lowercase letter, and a digit.
              </p>
            )}
          </div>

          <Button type="submit" className="w-full" isLoading={resetPassword.isPending}>
            Reset password
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={null}>
      <ResetPasswordForm />
    </Suspense>
  );
}

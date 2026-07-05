"use client";

import { CheckCircle2, Loader2, XCircle } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useRef } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useVerifyEmail } from "@/hooks/use-auth";

function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const verifyEmail = useVerifyEmail();
  // Guard against React 18 Strict Mode's double-invoke of effects in
  // development, which would otherwise fire this mutation twice.
  const hasAttempted = useRef(false);

  useEffect(() => {
    if (token && !hasAttempted.current) {
      hasAttempted.current = true;
      verifyEmail.mutate({ token });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  if (!token) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Invalid verification link</CardTitle>
          <CardDescription>This link is missing its verification token.</CardDescription>
        </CardHeader>
        <CardContent>
          <Link href="/dashboard">
            <Button className="w-full">Go to dashboard</Button>
          </Link>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="items-center text-center">
        {verifyEmail.isPending && (
          <Loader2 className="h-10 w-10 animate-spin text-primary" aria-hidden="true" />
        )}
        {verifyEmail.isSuccess && (
          <CheckCircle2 className="h-10 w-10 text-success" aria-hidden="true" />
        )}
        {verifyEmail.isError && <XCircle className="h-10 w-10 text-destructive" aria-hidden="true" />}

        <CardTitle>
          {verifyEmail.isPending && "Verifying your email..."}
          {verifyEmail.isSuccess && "Email verified"}
          {verifyEmail.isError && "Verification failed"}
        </CardTitle>
        <CardDescription>
          {verifyEmail.isSuccess && "Your email address has been confirmed."}
          {verifyEmail.isError &&
            "This link may be invalid or expired. Try resending it from your profile."}
        </CardDescription>
      </CardHeader>
      {(verifyEmail.isSuccess || verifyEmail.isError) && (
        <CardContent>
          <Link href="/dashboard">
            <Button className="w-full">Go to dashboard</Button>
          </Link>
        </CardContent>
      )}
    </Card>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={null}>
      <VerifyEmailContent />
    </Suspense>
  );
}

import Link from "next/link";

export default function NotFound() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-8 text-center">
      <h1 className="text-4xl font-bold">404</h1>
      <p className="text-muted-foreground">
        We couldn&apos;t find the page you&apos;re looking for.
      </p>
      <Link
        href="/"
        className="text-sm font-medium text-primary underline-offset-4 hover:underline"
      >
        Back to home
      </Link>
    </main>
  );
}

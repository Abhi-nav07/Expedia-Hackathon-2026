import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";

import { Providers } from "@/app/providers";

import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: {
    default: "Expedia Hackathon 2026",
    template: "%s | Expedia Hackathon 2026",
  },
  description:
    "Adaptive travel platform foundation for the Expedia Campus Hackathon.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "white" },
    { media: "(prefers-color-scheme: dark)", color: "black" },
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

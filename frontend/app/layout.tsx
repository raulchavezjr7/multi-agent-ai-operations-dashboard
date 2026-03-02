import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Ops Dashboard",
  description: "Multi-agent AI operations dashboard",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

import type { Metadata } from "next";
import { ThemeProvider } from "@/components/themeProvider";
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
      <ThemeProvider
        attribute="class"
        defaultTheme="system"
        enableSystem
        disableTransitionOnChange
      >
        <body>{children}</body>
      </ThemeProvider>
    </html>
  );
}

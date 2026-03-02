"use client";
import Link from "next/link";
import { cn } from "@/lib/utils";

export default function Sidebar() {
  return (
    <aside className="w-64 h-screen border-r bg-muted/30 p-4 flex flex-col gap-4">
      <h2 className="text-xl font-semibold"> AI Ops Dashboard </h2>
      <nav className="flex flex-col gap-2">
        <Link
          href="/dashboard/test-rag"
          className={cn(
            "px-3 py-2 rounded-md hover:bg-accent hover:text-accent-foreground",
          )}
        >
          Supervisor Test-Rag
        </Link>
        <Link
          href="/dashboard/database"
          className={cn(
            "px-3 py-2 rounded-md hover:bg-accent hover:text-accent-foreground",
          )}
        >
          Database Viewer
        </Link>
      </nav>
    </aside>
  );
}

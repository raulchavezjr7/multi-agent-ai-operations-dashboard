"use client";
import Link from "next/link";
import { ModeToggle } from "./modeToggle";
import { cn } from "@/lib/utils";

export default function Sidebar() {
  return (
    <aside className="w-64 min-h-screen border-r bg-muted/30 p-4 flex flex-col gap-4">
      <div className="flex items-center justify-around">
        <h2 className="text-xl font-semibold"> AI Ops Dashboard </h2>
        <ModeToggle />
      </div>
      <nav className="flex flex-col gap-2">
        <Link
          href="/dashboard/visualizations"
          className={cn(
            "px-3 py-2 rounded-md hover:bg-accent hover:text-accent-foreground",
          )}
        >
          Visualizations
        </Link>
        <Link
          href="/dashboard/test-rag"
          className={cn(
            "px-3 py-2 rounded-md hover:bg-accent hover:text-accent-foreground",
          )}
        >
          Supervisor Test with Rag
        </Link>
        <Link
          href="/dashboard/database"
          className={cn(
            "px-3 py-2 rounded-md hover:bg-accent hover:text-accent-foreground",
          )}
        >
          Database Viewer
        </Link>
        <Link
          href="/dashboard/daily-summary"
          className={cn(
            "px-3 py-2 rounded-md hover:bg-accent hover:text-accent-foreground",
          )}
        >
          Daily Summary
        </Link>
        <Link
          href="/dashboard/chat"
          className="px-3 py-2 rounded-md hover:bg-accent hover:text-accent-foreground"
        >
          Chatbot
        </Link>
      </nav>
    </aside>
  );
}

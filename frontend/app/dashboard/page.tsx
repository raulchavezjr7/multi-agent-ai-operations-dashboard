"use client";
import { useState } from "react";

export default function DashboardHome() {
  const [loading, setLoading] = useState(false);

  const handleDailyOverview = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/supervisor/overview", {
        method: "GET",
        headers: {
          accept: "application/json",
        },
      });
      const data = await res.json();

      console.log(data);
    } catch (err) {
      console.error("Error fetching supervisor overview:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-semibold">
        Welcome to the AI Ops Dashboard
      </h1>
      <p className="text-muted-foreground mt-2">
        Choose an option from the sidebar to begin.
      </p>

      <button
        onClick={handleDailyOverview}
        className="mt-4 px-4 py-2 bg-slate-900 text-white rounded hover:bg-slate-700"
      >
        Get Daily Overview
      </button>
      {loading && <p className="mt-4 text-sm">Loading…</p>}
    </div>
  );
}

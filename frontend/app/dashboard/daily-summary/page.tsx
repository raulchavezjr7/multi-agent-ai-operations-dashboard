"use client";

import { useEffect, useState } from "react";

type OverviewItem = {
  sales?: string;
  inventory?: string;
  support?: string;
  accounting?: string;
  operations?: string;
  supervisor?: string;
};

export default function DailySummaryPage() {
  const [overview, setOverview] = useState<OverviewItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOverview = async () => {
      const res = await fetch("http://127.0.0.1:8000/overview/all");
      const data = await res.json();
      setOverview(data);
      setLoading(false);
    };

    fetchOverview();
  }, []);

  if (loading) return <p className="p-4">Loading daily summary…</p>;

  const supervisor = overview.find((o) => o.supervisor);
  const sales = overview.find((o) => o.sales);
  const inventory = overview.find((o) => o.inventory);
  const support = overview.find((o) => o.support);
  const accounting = overview.find((o) => o.accounting);
  const operations = overview.find((o) => o.operations);

  return (
    <div className="p-6 space-y-6 ">
      <h1 className="text-3xl font-bold">Daily Summary</h1>

      <div className="p-6 shadow rounded-lg border bg-muted/30">
        <h2 className="text-xl font-semibold mb-2">Supervisor Overview</h2>
        <p className="whitespace-pre-line text-sm">{supervisor?.supervisor}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card title="Sales" content={sales?.sales} />
        <Card title="Inventory" content={inventory?.inventory} />
        <Card title="Support" content={support?.support} />
        <Card title="Accounting" content={accounting?.accounting} />
        <Card title="Operations" content={operations?.operations} />
      </div>
    </div>
  );
}

function Card({ title, content }: { title: string; content?: string }) {
  return (
    <div className="p-4 shadow rounded-lg border bg-muted/30">
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="whitespace-pre-line text-sm">{content}</p>
    </div>
  );
}

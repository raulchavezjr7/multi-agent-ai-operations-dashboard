"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";

interface OpsRow {
  region: string;
  total_customers: number;
}

interface SalesRow {
  region: string;
  revenue: number;
}

export default function VisualizationsPage() {
  const [ops, setOps] = useState<OpsRow[]>([]);
  const [sales, setSales] = useState<SalesRow[]>([]);

  useEffect(() => {
    async function load() {
      const opsRes = await fetch("http://localhost:8000/operations/summary");
      const opsJson = await opsRes.json();
      setOps(opsJson.operations_summary || []);

      const salesRes = await fetch("http://localhost:8000/sales/summary");
      const salesJson = await salesRes.json();
      setSales(salesJson.sales_summary || []);
    }
    load();
  }, []);

  const opsMax = Math.max(...ops.map((d) => d.total_customers), 0);
  const salesMax = Math.max(...sales.map((d) => d.revenue), 0);

  const formatRevenue = (value: number) =>
    new Intl.NumberFormat("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);

  return (
    <div className="w-full flex">
      <div className="max-w-xl space-y-6 mx-2">
        <h1 className="text-2xl font-semibold">Customers by Region</h1>
        <Card className="px-10 py-4 shadow-sm border rounded-xl bg-background">
          <div className="flex items-end justify-center gap-6 h-64">
            {ops.map((row, i) => {
              const height = (row.total_customers / opsMax) * 200;

              return (
                <div key={i} className="flex flex-col items-center">
                  <div
                    className="bg-blue-500 rounded-md transition-all duration-300"
                    style={{
                      width: "40px",
                      height: `${height}px`,
                    }}
                  ></div>

                  <span className="mt-2 text-sm font-medium">{row.region}</span>
                  <span className="text-xs text-muted-foreground">
                    {row.total_customers}
                  </span>
                </div>
              );
            })}
          </div>
        </Card>
      </div>
      <div className="max-w-xl space-y-6 mx-2">
        <h1 className="text-2xl font-semibold">Revenue by Region</h1>
        <Card className="px-10 py-4 shadow-sm border rounded-xl bg-background">
          <div className="flex items-end justify-center gap-6 h-64">
            {sales.map((row, i) => {
              const height = (row.revenue / salesMax) * 200;

              return (
                <div key={i} className="flex flex-col items-center">
                  <div
                    className="bg-green-700 rounded-md transition-all duration-300"
                    style={{
                      width: "40px",
                      height: `${height}px`,
                    }}
                  ></div>

                  <span className="mt-2 text-sm font-medium">{row.region}</span>
                  <span className="text-xs text-muted-foreground">
                    ${formatRevenue(row.revenue)}
                  </span>
                </div>
              );
            })}
          </div>
        </Card>
      </div>
    </div>
  );
}

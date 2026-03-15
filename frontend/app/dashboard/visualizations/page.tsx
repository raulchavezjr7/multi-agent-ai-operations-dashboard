"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { ChartDef, ChartRow } from "./renderers/types";
import { BarChart } from "./renderers/bar";
import { LineChart } from "./renderers/line";
import { AreaChart } from "./renderers/area";
import { ColumnLineChart } from "./renderers/columnLine";
import { Heatmap } from "./renderers/heatmap";
import { PieChart } from "./renderers/pie";

export default function VisualizationsPage() {
  const [charts, setCharts] = useState<ChartDef[]>([]);
  const [dataMap, setDataMap] = useState<Record<string, ChartRow[]>>({});

  useEffect(() => {
    async function loadCharts() {
      const res = await fetch("http://localhost:8000/charts");
      const json = await res.json();
      setCharts(json);
    }
    loadCharts();
  }, []);

  useEffect(() => {
    async function loadData() {
      const newData: Record<string, ChartRow[]> = {};

      for (const chart of charts) {
        const res = await fetch("http://localhost:8000/sql/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: chart.sql }),
        });

        const json = await res.json();

        if (json.columns && json.rows) {
          const formatted: ChartRow[] = json.rows.map((row: unknown[]) => {
            const obj: ChartRow = {};
            json.columns.forEach((col: string, idx: number) => {
              obj[col] = row[idx] as string | number;
            });
            return obj;
          });

          newData[chart.id] = formatted;
        }
      }

      setDataMap(newData);
    }

    if (charts.length > 0) loadData();
  }, [charts]);

  function renderChart(chart: ChartDef, rows: ChartRow[] | undefined) {
    if (!rows) return null;

    switch (chart.type) {
      case "bar":
        return <BarChart chart={chart} rows={rows} />;
      case "line":
        return <LineChart chart={chart} rows={rows} />;
      case "area":
        return <AreaChart chart={chart} rows={rows} />;
      case "column-line":
        return <ColumnLineChart chart={chart} rows={rows} />;
      case "heatmap":
        return <Heatmap chart={chart} rows={rows} />;
      case "pie":
        return <PieChart chart={chart} rows={rows} />;
      default:
        return <div>Unknown chart/graph type: {chart.type}</div>;
    }
  }

  return (
    <div className="w-full grid gap-6 grid-cols-[repeat(auto-fit,minmax(300px,500px))] justify-center">
      {charts.map((chart) => (
        <Card
          key={chart.id}
          className="py-4 px-2 shadow-sm border rounded-xl bg-muted/30"
        >
          <h2 className="text-lg font-semibold mb-4 text-center">
            {chart.name}
          </h2>

          {renderChart(chart, dataMap[chart.id])}
        </Card>
      ))}
    </div>
  );
}

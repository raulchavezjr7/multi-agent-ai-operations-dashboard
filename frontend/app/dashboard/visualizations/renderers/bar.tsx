import { ChartDef, ChartRow } from "./types";

interface ChartProps {
  chart: ChartDef;
  rows: ChartRow[];
}

export function BarChart({ chart, rows }: ChartProps) {
  if (!rows || rows.length === 0) return null;

  const maxValue = Math.max(
    ...rows.map((r) => Number(r[chart.yField] ?? 0)),
    0,
  );

  return (
    <div className="flex items-end justify-center gap-3 sm:gap-6 h-64 py-2 overflow-hidden">
      {rows.map((row, i) => {
        const value = Number(row[chart.yField] ?? 0);
        const heightPx = maxValue > 0 ? (value / maxValue) * 200 : 0;

        return (
          <div
            key={i}
            className="flex flex-col items-center w-8 sm:w-12 flex-shrink-0"
          >
            <div
              className="rounded-md transition-all duration-300 w-full"
              style={{
                height: `${heightPx}px`,
                backgroundColor: chart.color,
              }}
            />

            <span className="mt-2 text-[10px] sm:text-sm font-medium break-words text-center">
              {String(row[chart.xField])}
            </span>

            <span className="text-[9px] sm:text-xs text-muted-foreground">
              {value.toLocaleString()}
            </span>
          </div>
        );
      })}
    </div>
  );
}

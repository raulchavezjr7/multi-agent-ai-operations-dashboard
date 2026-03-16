import { ChartDef, ChartRow } from "./types";

interface HeatmapProps {
  chart: ChartDef;
  rows: ChartRow[];
}

export function Heatmap({ chart, rows }: HeatmapProps) {
  if (!rows || rows.length === 0) return null;

  const maxValue = Math.max(
    ...rows.map((r) => Number(r[chart.yField] ?? 0)),
    0,
  );

  function getHeatColor(intensity: number): string {
    if (intensity < 0.5) {
      const ratio = intensity / 0.5;
      return `rgb(
        ${Math.round(34 + (250 - 34) * ratio)},
        ${Math.round(197 + (204 - 197) * ratio)},
        ${Math.round(94 + (21 - 94) * ratio)}
      )`;
    } else {
      const ratio = (intensity - 0.5) / 0.5;
      return `rgb(
        ${Math.round(250 + (220 - 250) * ratio)},
        ${Math.round(204 + (38 - 204) * ratio)},
        ${Math.round(21 + (38 - 21) * ratio)}
      )`;
    }
  }

  return (
    <div style={{ width: "100%", height: "250px" }}>
      <div className="grid grid-cols-3 gap-2 p-4">
        {rows.map((row, i) => {
          const value = Number(row[chart.yField] ?? 0);
          const intensity = maxValue > 0 ? value / maxValue : 0;

          return (
            <div
              key={chart.id + "_heat_" + i}
              className="
              rounded 
              text-center 
              text-white 
              flex 
              flex-col 
              items-center 
              justify-center 
              p-2 
              min-h-[60px]
              break-words 
              text-xs 
              sm:text-sm
            "
              style={{ backgroundColor: getHeatColor(intensity) }}
            >
              <span className="font-medium">{String(row[chart.xField])}</span>
              <span className="opacity-90">
                {value.toLocaleString("en-US")}
              </span>
            </div>
          );
        })}
      </div>
      <div className="flex flex-col items-center mt-3">
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-500">Less</span>
          <div className="h-3 w-32 rounded bg-gradient-to-r from-green-500 via-yellow-400 to-red-600"></div>
          <span className="text-xs text-gray-500">More</span>
        </div>
        <p className="text-[10px] text-gray-400 mt-1">
          Darker colors indicate higher density
        </p>
      </div>
    </div>
  );
}

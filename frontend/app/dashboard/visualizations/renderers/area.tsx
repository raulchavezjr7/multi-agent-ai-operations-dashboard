import { ChartDef, ChartRow } from "./types";

interface AreaChartProps {
  chart: ChartDef;
  rows: ChartRow[];
}

export function AreaChart({ chart, rows }: AreaChartProps) {
  if (!rows || rows.length === 0) return null;

  const chartWidth = 300;
  const chartHeight = 180;

  const maxValue = Math.max(
    ...rows.map((r) => Number(r[chart.yField] ?? 0)),
    0,
  );

  const points = rows
    .map((row, i) => {
      const x = 40 + i * (chartWidth / (rows.length - 1));
      const y =
        20 +
        (chartHeight -
          (Number(row[chart.yField] ?? 0) / maxValue) * chartHeight);
      return `${x},${y}`;
    })
    .join(" ");

  const yTicks = [0, maxValue / 2, maxValue];

  return (
    <svg width="100%" height="260" viewBox="0 0 360 240">
      {rows.map((row, i) => {
        const x = 40 + i * (chartWidth / (rows.length - 1));
        return (
          <text
            key={"x_tick_" + i}
            x={x}
            y={225}
            textAnchor="middle"
            className="text-[10px] fill-gray-500"
          >
            {String(row[chart.xField])}
          </text>
        );
      })}

      {yTicks.map((tick, i) => {
        const y = 20 + (chartHeight - (tick / maxValue) * chartHeight);
        return (
          <text
            key={"y_tick_" + i}
            x={10}
            y={y + 3}
            textAnchor="start"
            className="text-[10px] fill-gray-500"
          >
            {Math.round(tick)}
          </text>
        );
      })}

      <polygon
        fill={(chart.color ?? "#22c55e") + "55"}
        stroke={chart.color ?? "#22c55e"}
        strokeWidth="2"
        points={`40,200 ${points} 340,200`}
      />
    </svg>
  );
}

import { ChartDef, ChartRow } from "./types";

interface PieChartProps {
  chart: ChartDef;
  rows: ChartRow[];
}

export function PieChart({ chart, rows }: PieChartProps) {
  if (!rows || rows.length === 0) return <div>No data</div>;

  const total = rows.reduce((sum, r) => sum + Number(r[chart.yField] ?? 0), 0);

  if (total === 0) return <div>No data</div>;
  if (rows.length === 1) return <div>Pie chart needs 2+ categories</div>;

  const slices = rows.map((row) => {
    const value = Number(row[chart.yField] ?? 0);
    const angle = (value / total) * Math.PI * 2;
    return { value, angle };
  });

  const cumulativeAngles = slices.reduce<number[]>((acc, slice, i) => {
    if (i === 0) return [slice.angle];
    return [...acc, acc[i - 1] + slice.angle];
  }, []);

  return (
    <div className="flex flex-col items-center w-full">
      <svg width="100%" height="250" viewBox="0 0 200 200">
        {slices.map((slice, i) => {
          const startAngle = i === 0 ? 0 : cumulativeAngles[i - 1];
          const endAngle = cumulativeAngles[i];

          const x1 = 100 + 100 * Math.cos(startAngle);
          const y1 = 100 + 100 * Math.sin(startAngle);

          const x2 = 100 + 100 * Math.cos(endAngle);
          const y2 = 100 + 100 * Math.sin(endAngle);

          const largeArc = slice.angle > Math.PI ? 1 : 0;

          return (
            <path
              key={`${chart.id}_slice_${i}`}
              d={`M100,100 L${x1},${y1} A100,100 0 ${largeArc} 1 ${x2},${y2} Z`}
              fill={chart.colors?.[i % chart.colors.length] ?? "#ccc"}
            />
          );
        })}
      </svg>

      <div className="flex flex-wrap justify-center gap-4 mt-4 px-4 py-2 bg-white/20 rounded-md">
        {rows.map((row, i) => (
          <div key={i} className="flex items-center gap-2">
            <div
              className="w-4 h-4 rounded-sm border border-black/20"
              style={{
                backgroundColor:
                  chart.colors?.[i % chart.colors.length] ?? "#ccc",
              }}
            />
            <span className="text-sm text-black">
              {String(row[chart.xField])}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

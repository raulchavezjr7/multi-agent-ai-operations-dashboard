export interface ChartDef {
  id: string;
  name: string;
  sql: string;
  type: string;
  xField: string;
  yField: string;
  color?: string;
  colors?: string[];
  span: number;
}

export type ChartRow = Record<string, string | number>;

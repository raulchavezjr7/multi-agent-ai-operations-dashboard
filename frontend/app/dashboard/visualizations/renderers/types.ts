export interface ChartDef {
  id: string;
  name: string;
  sql: string;
  type: string;
  xField: string;
  yField: string;
  color?: string;
  colors?: string[];
}

export const defaultChartDef: ChartDef = {
  id: "",
  name: "",
  sql: "",
  type: "",
  xField: "",
  yField: "",
};

export type ChartRow = Record<string, string | number>;

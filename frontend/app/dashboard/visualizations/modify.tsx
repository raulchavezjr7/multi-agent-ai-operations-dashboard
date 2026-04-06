import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogClose,
} from "@/components/ui/dialog";
import { SquarePen } from "lucide-react";
import { ChartDef, defaultChartDef } from "./renderers/types";
import { LlmAddDialog } from "./llmAddDialog";

interface ModifyGraphDialogProps {
  charts: ChartDef[];
  onEdit?: (chart: ChartDef) => void;
  onDelete?: (id: string) => void;
  onCreate?: (spec: ChartDef) => void;
  editingChart: ChartDef | null;
  setEditingChart: (chart: ChartDef | null) => void;
}

export function ModifyGraphDialog({
  charts,
  onEdit,
  onDelete,
  onCreate,
  editingChart,
  setEditingChart,
}: ModifyGraphDialogProps) {
  //const [editingChart, setEditingChart] = useState<ChartDef>(defaultChartDef);
  const [deleteChart, setDeleteChart] = useState<ChartDef>(defaultChartDef);
  const [addChart, setAddChart] = useState(false);

  return (
    <>
      <Dialog>
        <DialogTrigger asChild>
          <Button variant="outline" size="sm" className="w-fit">
            <SquarePen className="mr-1 h-4 w-4" />
            Customize View
          </Button>
        </DialogTrigger>

        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Modify</DialogTitle>
            <DialogDescription>
              Manage the visualizations displayed on your dashboard.
            </DialogDescription>
          </DialogHeader>

          <div className="py-4 space-y-3">
            {charts.map((chart) => (
              <div
                key={chart.id}
                className="flex items-center justify-between border p-2 rounded-md"
              >
                <span className="text-sm">{chart.name}</span>

                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => setEditingChart(chart)}
                  >
                    Edit
                  </Button>

                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => setDeleteChart(chart)}
                  >
                    Delete
                  </Button>
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-end mb-4">
            <Button onClick={() => setAddChart(!addChart)}>Create New</Button>
          </div>
          <DialogFooter className="flex justify-end gap-2">
            <DialogClose asChild>
              <Button type="button" variant="secondary">
                Cancel
              </Button>
            </DialogClose>

            <DialogClose asChild>
              <Button type="submit">Done</Button>
            </DialogClose>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      {addChart && (
        <LlmAddDialog
          onChartSpecGenerated={(spec) => {
            onCreate?.(spec); // save it
            setEditingChart(spec); // immediately open edit dialog
          }}
        />
      )}
      {editingChart ? (
        <Dialog open={true} onOpenChange={() => setEditingChart(null)}>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle> Edit Chart</DialogTitle>
              <DialogDescription>
                Modify the settings for <strong>{editingChart.name}</strong>.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              <div>
                <label className="text-sm font-medium">Name</label>
                <input
                  type="text"
                  className="w-full border rounded p-2"
                  value={editingChart.name ?? ""}
                  onChange={(e) =>
                    setEditingChart({ ...editingChart, name: e.target.value })
                  }
                />
              </div>
              <div>
                <label className="text-sm font-medium">SQL</label>
                <input
                  type="text"
                  className="w-full border rounded p-2"
                  value={editingChart.sql ?? ""}
                  onChange={(e) =>
                    setEditingChart({ ...editingChart, sql: e.target.value })
                  }
                />
              </div>
              <div>
                <label className="text-sm font-medium">Chart Type</label>
                <Select
                  value={editingChart.type}
                  onValueChange={(value) =>
                    setEditingChart({ ...editingChart, type: value })
                  }
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select chart type" />
                  </SelectTrigger>

                  <SelectContent>
                    <SelectItem value="bar">Bar</SelectItem>
                    <SelectItem value="line">Line</SelectItem>
                    <SelectItem value="area">Area</SelectItem>
                    <SelectItem value="column-line">Column Line</SelectItem>
                    <SelectItem value="heatmap">Heatmap</SelectItem>
                    <SelectItem value="pie">Pie</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium">X-Field</label>
                <input
                  type="text"
                  className="w-full border rounded p-2"
                  value={editingChart.xField ?? ""}
                  onChange={(e) =>
                    setEditingChart({ ...editingChart, xField: e.target.value })
                  }
                />
              </div>
              <div>
                <label className="text-sm font-medium">Y-Field</label>
                <input
                  type="text"
                  className="w-full border rounded p-2"
                  value={editingChart.yField ?? ""}
                  onChange={(e) =>
                    setEditingChart({ ...editingChart, yField: e.target.value })
                  }
                />
              </div>
              {editingChart.type === "heatmap" ||
              editingChart.type === "pie" ? null : (
                <div>
                  <label className="text-sm font-medium">Color</label>
                  <div className="flex items-center gap-3">
                    <div
                      className="w-8 h-8 rounded border cursor-pointer"
                      style={{ backgroundColor: editingChart.color }}
                      onClick={() =>
                        document.getElementById("colorPicker")?.click()
                      }
                    />
                    <input
                      id="colorPicker"
                      type="color"
                      className="hidden"
                      value={editingChart.color ?? "#000000"}
                      onChange={(e) =>
                        setEditingChart({
                          ...editingChart,
                          color: e.target.value,
                        })
                      }
                    />
                    <span className="text-sm text-gray-600">
                      {editingChart.color}
                    </span>
                  </div>
                </div>
              )}
              {editingChart.type === "pie" ? (
                <div className="space-y-2">
                  <label className="text-sm font-medium">Colors</label>
                  <div className="space-y-3">
                    {(editingChart.colors ?? []).map((color, index) => (
                      <div key={index} className="flex items-center gap-3">
                        <div
                          className="w-8 h-8 rounded border cursor-pointer"
                          style={{ backgroundColor: color }}
                          onClick={() =>
                            document
                              .getElementById(`colorPicker-${index}`)
                              ?.click()
                          }
                        />
                        <input
                          id={`colorPicker-${index}`}
                          type="color"
                          className="hidden"
                          value={color}
                          onChange={(e) => {
                            const newColors = [...(editingChart.colors ?? [])];
                            newColors[index] = e.target.value;
                            setEditingChart({
                              ...editingChart,
                              colors: newColors,
                            });
                          }}
                        />
                        <span className="text-sm text-gray-600 w-24">
                          {color}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>

            <DialogFooter>
              <Button variant="secondary" onClick={() => setEditingChart(null)}>
                Cancel
              </Button>

              <Button
                onClick={() => {
                  onEdit?.(editingChart);
                  setEditingChart(null);
                }}
              >
                Save
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      ) : null}
      {deleteChart === defaultChartDef ? null : (
        <Dialog
          open={true}
          onOpenChange={() => setDeleteChart(defaultChartDef)}
        >
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Delete Chart</DialogTitle>
              <DialogDescription>
                Are you sure you want to delete{" "}
                <strong>{deleteChart.name}</strong>? This action cannot be
                undone.
              </DialogDescription>
            </DialogHeader>

            <DialogFooter className="flex justify-end gap-2">
              <Button
                variant="secondary"
                onClick={() => setDeleteChart(defaultChartDef)}
              >
                Cancel
              </Button>

              <Button
                variant="destructive"
                onClick={() => {
                  onDelete?.(deleteChart.id);
                  setDeleteChart(defaultChartDef);
                }}
              >
                Delete
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </>
  );
}

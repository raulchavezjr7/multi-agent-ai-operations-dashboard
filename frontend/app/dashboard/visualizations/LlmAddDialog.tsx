import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { ChartDef } from "./renderers/types";

interface LlmAddDialogProps {
  onChartSpecGenerated: (spec: ChartDef) => void;
}

export function LlmAddDialog({ onChartSpecGenerated }: LlmAddDialogProps) {
  const [open, setOpen] = useState(true);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<
    { role: "user" | "assistant"; content: string }[]
  >([]);
  const [generatedSpec, setGeneratedSpec] = useState<ChartDef | null>(null);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const newMessages = [
      ...messages,
      { role: "user", content: input } as const,
    ];
    setMessages(newMessages);
    setInput("");
    setLoading(true);
    console.log(newMessages);
    const res = await fetch(
      `http://localhost:8000/supervisor/create-chart-chat`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: newMessages }),
      },
    );

    const data = await res.json();
    setLoading(false);

    if (data.response) {
      setGeneratedSpec(data.response);
      setMessages([
        ...newMessages,
        { role: "assistant", content: "Here is the chart I generated." },
      ]);
    }
    console.log(data);
    console.log(messages);
  };

  const handleConfirm = () => {
    if (!generatedSpec) return;
    onChartSpecGenerated(generatedSpec);
    setOpen(false);
    setMessages([]);
    setGeneratedSpec(null);
  };
  return (
    <>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Create a New Chart</DialogTitle>
            <DialogDescription>
              Describe the chart you want. The assistant will generate a NoSQL
              chart entry.
            </DialogDescription>
          </DialogHeader>

          <div className="border rounded p-2 h-48 overflow-y-auto text-sm space-y-2">
            {messages.map((m, i) => (
              <div
                key={i}
                className={
                  m.role === "user"
                    ? "text-right"
                    : "text-left text-muted-foreground"
                }
              >
                <span className="inline-block bg-muted px-2 py-1 rounded">
                  {m.content}
                </span>
              </div>
            ))}
          </div>

          <Textarea
            placeholder="Describe your chart..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />

          <Button onClick={sendMessage} disabled={loading}>
            {loading ? "Thinking..." : "Send"}
          </Button>

          {generatedSpec && (
            <div className="border rounded p-2 bg-muted text-xs max-h-48 overflow-y-auto">
              <pre>{JSON.stringify(generatedSpec, null, 2)}</pre>
            </div>
          )}
          <DialogFooter>
            <Button variant="secondary" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleConfirm} disabled={!generatedSpec}>
              Save Chart
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}

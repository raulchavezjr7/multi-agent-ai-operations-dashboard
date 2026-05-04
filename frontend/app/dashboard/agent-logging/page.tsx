"use client";

import { useCallback, useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";

type AgentLog = {
  id: number;
  timestamp: string;
  agent_name: string;
  agent_role: string;
  label: string;
  request_type: string;
  message_overview: string;
  prompt_tokens: number;
  completion_tokens: number;
  details_json?: string | null;
};

export default function AgentLoggingPage() {
  const [logs, setLogs] = useState<AgentLog[]>([]);
  const [agentFilter, setAgentFilter] = useState("all");
  const [labelFilter, setLabelFilter] = useState("all");
  const [typeFilter, setTypeFilter] = useState("all");
  const [loading, setLoading] = useState(false);

  const fetchLogs = useCallback(async () => {
    setLoading(true);

    const params = new URLSearchParams();
    if (agentFilter !== "all") params.set("agent_name", agentFilter);
    if (labelFilter !== "all") params.set("label", labelFilter);
    if (typeFilter !== "all") params.set("request_type", typeFilter);

    const res = await fetch(
      `http://localhost:8000/agent-logs?${params.toString()}`,
    );
    let data = await res.json();

    if (!Array.isArray(data)) {
      console.warn("Unexpected logs response:", data);
      data = [];
    }

    setLogs(data);
    setLoading(false);
  }, [agentFilter, labelFilter, typeFilter]);

  useEffect(() => {
    const load = async () => {
      await fetchLogs();
    };
    load();
  }, [agentFilter, labelFilter, typeFilter]);

  const total = logs.length;
  const errors = logs.filter((l) => l.label === "ERROR").length;
  const totalPromptTokens = logs.reduce(
    (sum, l) => sum + (l.prompt_tokens || 0),
    0,
  );
  const totalCompletionTokens = logs.reduce(
    (sum, l) => sum + (l.completion_tokens || 0),
    0,
  );
  const totalTokens = totalPromptTokens + totalCompletionTokens;

  return (
    <div className="flex flex-col gap-6 h-full">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Agent Logging</h1>
          <p className="text-sm text-muted-foreground">
            Monitor agent activity, errors, and internal operations.
          </p>
        </div>

        <Button variant="outline" onClick={fetchLogs} disabled={loading}>
          {loading ? "Refreshing..." : "Refresh"}
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="p-4 bg-muted/30">
          <p className="text-xs text-muted-foreground">Total Logs</p>
          <p className="text-2xl font-semibold">{total}</p>
        </Card>
        <Card className="p-4 bg-muted/30">
          <p className="text-xs text-muted-foreground">Prompt Tokens</p>
          <p className="text-2xl font-semibold text-blue-500">
            {totalPromptTokens}
          </p>
        </Card>
        <Card className="p-4 bg-muted/30">
          <p className="text-xs text-muted-foreground">Completion Tokens</p>
          <p className="text-2xl font-semibold text-amber-500">
            {totalCompletionTokens}
          </p>
        </Card>

        <Card className="p-4 bg-muted/30">
          <p className="text-xs text-muted-foreground">Total Tokens</p>
          <p className="text-2xl font-semibold text-purple-500">
            {totalTokens}
          </p>
        </Card>

        <Card className="p-4 bg-muted/30">
          <p className="text-xs text-muted-foreground">Errors</p>
          <p className="text-2xl font-semibold text-red-500">{errors}</p>
        </Card>
      </div>

      <div className="flex flex-1 gap-4 min-h-0">
        <Card className="w-full max-w-xs p-4 space-y-4 bg-muted/30">
          <div>
            <p className="text-sm font-medium mb-1">Filter by Agent</p>
            <Select value={agentFilter} onValueChange={setAgentFilter}>
              <SelectTrigger>
                <SelectValue placeholder="All agents" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Agents</SelectItem>
                <SelectItem value="Supervisor Agent">
                  Supervisor Agent
                </SelectItem>
                <SelectItem value="Accounting Agent">
                  Accounting Agent
                </SelectItem>
                <SelectItem value="Inventory Agent">Inventory Agent</SelectItem>
                <SelectItem value="Operations Agent">
                  Operations Agent
                </SelectItem>
                <SelectItem value="Sales Agent">Sales Agent</SelectItem>
                <SelectItem value="Support Agent">Support Agent</SelectItem>
                <SelectItem value="Rag Agent">RAG Agent</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <p className="text-sm font-medium mb-1">Filter by Label</p>
            <Select value={labelFilter} onValueChange={setLabelFilter}>
              <SelectTrigger>
                <SelectValue placeholder="All Label" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All</SelectItem>
                <SelectItem value="Processed">Processed</SelectItem>
                <SelectItem value="ERROR">Error</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <p className="text-sm font-medium mb-1">Request Type</p>
            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger>
                <SelectValue placeholder="All Types" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All</SelectItem>
                <SelectItem value="prompt">Prompt</SelectItem>
                <SelectItem value="response">Response</SelectItem>
                <SelectItem value="error">Error</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </Card>

        <Card className="flex-1 p-0 flex flex-col min-h-0 bg-muted/30">
          <div className="border-b px-4 py-2 flex items-center justify-between">
            <p className="text-sm font-medium">Log Stream</p>
            <p className="text-xs text-muted-foreground">
              Showing {logs.length} entries
            </p>
          </div>

          <ScrollArea className="flex-1 px-4 py-2 bg-muted/30">
            <div className="space-y-2">
              {logs.map((log) => {
                const details =
                  log.details_json && log.details_json !== "null"
                    ? JSON.parse(log.details_json)
                    : null;
                const tokens =
                  log.prompt_tokens !== 0
                    ? log.prompt_tokens
                    : log.completion_tokens !== 0
                      ? log.completion_tokens
                      : 0;

                return (
                  <div
                    key={log.id}
                    className={`rounded-md border px-3 py-2 text-sm bg-background/60
                      ${log.label === "ERROR" ? "border-red-500/60" : ""}`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Badge
                          variant="outline"
                          className={
                            log.label === "ERROR"
                              ? "border-red-500 text-red-500"
                              : log.label === "Processed"
                                ? "border-emerald-500 text-emerald-500"
                                : "border-slate-500 text-slate-500"
                          }
                        >
                          {log.label === "ERROR" ? "Error" : log.label}
                        </Badge>
                        <Badge
                          variant="outline"
                          className={`capitalize ${
                            log.request_type === "error"
                              ? "border-red-500 text-red-500"
                              : log.request_type === "prompt"
                                ? "border-emerald-500 text-blue-500"
                                : "border-slate-500 text-purple-500"
                          }`}
                        >
                          {log.request_type}
                        </Badge>
                        <span className="font-medium">{log.agent_name}</span>
                        <span className="text-xs text-muted-foreground">
                          ({log.agent_role})
                        </span>
                      </div>

                      <span className="text-xs text-muted-foreground">
                        {new Date(log.timestamp).toLocaleString()}
                      </span>
                    </div>

                    <p className="mt-1">{log.message_overview}</p>

                    {details && (
                      <details className="mt-1 text-xs">
                        <summary className="cursor-pointer text-muted-foreground">
                          Details
                        </summary>
                        <pre className="mt-1 whitespace-pre-wrap text-[11px] bg-muted p-2 rounded">
                          {JSON.stringify(details, null, 2)}
                        </pre>
                      </details>
                    )}
                    <details className="mt-1 text-xs">
                      <summary className="cursor-pointer text-muted-foreground">
                        Tokens
                      </summary>
                      <pre className="mt-1 whitespace-pre-wrap text-[11px] bg-muted p-2 rounded">
                        Total Tokens:{" "}
                        {tokens === 0
                          ? "Tokens are only calculated in successful request or response message"
                          : tokens}
                      </pre>
                    </details>
                  </div>
                );
              })}

              {logs.length === 0 && !loading && (
                <p className="text-sm text-muted-foreground">
                  No logs found for the selected filters.
                </p>
              )}
            </div>
          </ScrollArea>
        </Card>
      </div>
    </div>
  );
}

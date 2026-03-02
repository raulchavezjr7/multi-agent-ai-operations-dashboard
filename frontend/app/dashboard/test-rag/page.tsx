"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function TestRagPage() {
  const [response, setResponse] = useState("");

  async function runTest() {
    const res = await fetch("http://localhost:8000/supervisor/test-rag");
    const data = await res.json();
    setResponse(data.supervisor_response);
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Supervisor Test‑RAG</h1>
      <Button onClick={runTest}>Run Test</Button>
      {response && <Card className="p-4 whitespace-pre-wrap">{response}</Card>}
    </div>
  );
}

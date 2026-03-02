"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface QueryResult {
  columns: string[];
  rows: (string | number | boolean | null)[][];
}

export default function DatabasePage() {
  const [query, setQuery] = useState("SELECT * FROM inventory LIMIT 20");
  const [data, setData] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);

  async function runQuery() {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/sql/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const json = await res.json();
      setData(json);
    } catch (err) {
      console.error("Query failed", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Database Viewer</h1>
      <Textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="h-32"
      ></Textarea>
      <Button onClick={runQuery}>{loading ? "Running..." : "Run Query"}</Button>

      {data ? (
        <Card className="p-4">
          <Table>
            <TableHeader>
              <TableRow>
                {data.columns.map((col) => (
                  <TableHead key={col}>{col}</TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.rows.map((row, i) => (
                <TableRow key={i}>
                  {row.map((cell, j) => (
                    <TableCell key={j}>{String(cell)}</TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      ) : (
        <></>
      )}
    </div>
  );
}

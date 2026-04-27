"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
export default function RagAdminPage() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [initializing, setInitializing] = useState(false);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    setStatus(null);
    setError(null);
    setFiles(e.target.files);
  }

  async function handleUpload() {
    if (!files || files.length === 0) {
      setError("Please select at least one .txt or .pdf file.");
      return;
    }

    const formData = new FormData();
    Array.from(files).forEach((file) => {
      const ext = file.name.split(".").pop()?.toLowerCase();
      if (ext !== "txt" && ext !== "pdf") {
        return;
      }
      formData.append("files", file);
    });

    if (!formData.has("files")) {
      setError("Only .txt and .pdf files are allowed.");
      return;
    }

    setUploading(true);
    setError(null);
    setStatus(null);

    try {
      const res = await fetch("http://localhost:8000/rag/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Upload failed");
      }

      const data = await res.json();
      setStatus(`Uploaded: ${data.saved_files.join(", ")}`);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Upload failed");
      }
    } finally {
      setUploading(false);
    }
  }

  async function handleInitRag() {
    setInitializing(true);
    setError(null);
    setStatus(null);

    try {
      const res = await fetch("http://localhost:8000/rag/reload", {
        method: "POST",
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "RAG initialization failed");
      }

      setStatus("RAG initialized. New documents are now indexed.");
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("RAG initialization failed");
      }
    } finally {
      setInitializing(false);
    }
  }

  return (
    <div className="flex flex-col gap-6 max-w-2xl mx-auto py-8">
      <h1 className="text-2xl font-semibold">RAG Document Manager</h1>

      <Card className="p-4 space-y-4">
        <div>
          <h2 className="font-medium mb-1">1. Upload documents</h2>
          <p className="text-sm text-muted-foreground">
            Supported types: <span className="font-mono">.txt</span>
            {" and "}
            <span className="font-mono">.pdf</span>
          </p>
        </div>

        <Input
          type="file"
          multiple
          accept=".txt,.pdf"
          onChange={handleFileChange}
          className="
            cursor-pointer
            bg-slate-100
            dark:bg-gray-800
            hover:bg-gray-400
            dark:hover:bg-gray-700
            "
        />

        <Button onClick={handleUpload} disabled={uploading}>
          {uploading ? "Uploading..." : "Upload selected files"}
        </Button>

        {uploading && (
          <div className="flex justify-center py-2">
            <div className="animate-spin h-5 w-5 border-2 border-gray-400 border-t-transparent rounded-full"></div>
          </div>
        )}

        {status && (
          <p className="text-sm text-emerald-600 whitespace-pre-line">
            {status}
          </p>
        )}
        {error && (
          <p className="text-sm text-red-600 whitespace-pre-line">{error}</p>
        )}
      </Card>

      <Card className="p-4 space-y-4">
        <div>
          <h2 className="font-medium mb-1">2. Initialize RAG</h2>
          <p className="text-sm text-muted-foreground">
            After uploading new documents, click this to reload and reindex them
            into the RAG pipeline.
          </p>
        </div>

        <Button
          onClick={handleInitRag}
          variant="outline"
          disabled={initializing}
        >
          {initializing ? "Initializing..." : "Initialize RAG"}
        </Button>

        {initializing && (
          <div className="flex justify-center py-2">
            <div className="animate-spin h-5 w-5 border-2 border-gray-400 border-t-transparent rounded-full"></div>
          </div>
        )}
      </Card>
    </div>
  );
}

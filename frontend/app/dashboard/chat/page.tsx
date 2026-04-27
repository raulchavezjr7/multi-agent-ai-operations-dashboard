"use client";

import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";

export default function ChatPage() {
  const [messages, setMessages] = useState<{ role: string; text: string }[]>(
    [],
  );
  const [input, setInput] = useState("");
  const [ragMode, setRagMode] = useState("full-rag");
  const modelLoadedRef = useRef(false);
  const [modelLoading, setModelLoading] = useState(false);
  const [botThinking, setBotThinking] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const unload = () => {
      navigator.sendBeacon(
        "http://localhost:8000/chat/session/unload",
        new Blob([], { type: "application/json" }),
      );
    };

    window.addEventListener("beforeunload", unload);
    return () => {
      unload();
      window.removeEventListener("beforeunload", unload);
    };
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function ensureModelLoaded() {
    if (modelLoadedRef.current) return;

    setModelLoading(true);

    await fetch("http://localhost:8000/chat/session/load", {
      method: "POST",
    });

    modelLoadedRef.current = true;
    setModelLoading(false);
  }

  async function sendMessage() {
    if (!input.trim()) return;

    await ensureModelLoaded();

    const userMsg = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setBotThinking(true);

    const apiUrl =
      ragMode === "full-rag"
        ? "http://localhost:8000/chat/full-rag"
        : ragMode === "semi-rag"
          ? "http://localhost:8000/chat/semi-rag"
          : "http://localhost:8000/chat/no-rag";

    console.log(apiUrl);

    const res = await fetch(apiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userMsg.text }),
    });

    const data = await res.json();

    setMessages((prev) => [...prev, { role: "bot", text: data.response }]);
    setBotThinking(false);
    //console.log(messages);
    //console.log(data.response);
  }

  return (
    <div className="flex flex-col h-[95vh] space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">CHATbot</h1>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button>Mode: {ragMode.toUpperCase()}</Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => setRagMode("full-rag")}>
              Full-RAG
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setRagMode("semi-rag")}>
              Semi‑RAG
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setRagMode("no-rag")}>
              No‑RAG
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <Card className="flex-1 p-4 overflow-y-auto space-y-2 min-h-0 bg-muted/30">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex items-end gap-2 ${m.role === "user" ? "flex-row-reverse" : "flex-row"}`}
          >
            <div
              className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white ${
                m.role === "user" ? "bg-blue-500" : "bg-slate-500"
              } shadow-sm`}
            >
              {m.role === "user" ? "U" : "AI"}
            </div>
            <div
              className={`p-3 shadow-sm max-w-[75%] ${
                m.role === "user"
                  ? "rounded-2xl rounded-br-none"
                  : "rounded-2xl rounded-bl-none"
              }`}
              style={{
                backgroundColor: m.role === "user" ? "#3B82F6" : "#6B7280",
                color: "white",
              }}
            >
              <p className="text-sm md:text-base leading-relaxed whitespace-pre-wrap">
                {m.text}
              </p>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </Card>

      {modelLoading && (
        <div className="text-center text-sm text-gray-500 py-2">
          Loading AI model… this may take a moment
        </div>
      )}

      {botThinking && !modelLoading && (
        <div className="flex items-center gap-2 text-gray-500 text-sm py-2">
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-300"></div>
          <span>Thinking…</span>
        </div>
      )}

      <div className="flex gap-2">
        <Input
          className="bg-white dark:bg-gray-800"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
        />
        <Button onClick={sendMessage}>Send</Button>
      </div>
    </div>
  );
}

"use client";

import { useState } from "react";

interface FollowupBarProps {
  visible: boolean;
  /** Called with the question and a fn to stream-append text to the report */
  onSubmit: (question: string, appendToReport: (section: string) => void) => void;
  isLoading: boolean;
}

export function FollowupBar({ visible, onSubmit, isLoading }: FollowupBarProps) {
  const [question, setQuestion] = useState("");
  const [appendBuffer, setAppendBuffer] = useState("");

  if (!visible) return null;

  const handleSubmit = () => {
    if (!question.trim() || isLoading) return;
    const q = question.trim();
    setQuestion("");

    // appendToReport: each incremental chunk appended to local buffer displayed below
    onSubmit(q, (section: string) => {
      setAppendBuffer((prev) => prev + section);
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div
      className="border-t flex-shrink-0"
      style={{
        backgroundColor: "#0a0a0a",
        borderColor: "oklch(0.16 0 0)",
      }}
    >
      {/* Streamed followup answer section */}
      {appendBuffer && (
        <div
          className="px-6 pt-4 pb-2 max-h-48 overflow-y-auto"
          style={{ borderBottom: "1px solid oklch(0.14 0 0)" }}
        >
          <div
            className="rounded-lg border p-4"
            style={{
              backgroundColor: "oklch(0.10 0 0)",
              borderColor: "oklch(0.18 0 0)",
            }}
          >
            <p className="text-[10px] font-medium mb-2" style={{ color: "#d4830a" }}>
              追问结果
            </p>
            <p className="text-xs text-zinc-400 whitespace-pre-wrap leading-relaxed">
              {appendBuffer}
            </p>
          </div>
        </div>
      )}

      {/* Input row */}
      <div className="px-6 py-4">
        <div
          className="flex items-center gap-3 rounded-lg border px-4 py-2.5 transition-colors"
          style={{
            backgroundColor: "oklch(0.11 0 0)",
            borderColor: "oklch(0.22 0 0)",
          }}
        >
          <svg
            className="w-4 h-4 flex-shrink-0"
            style={{ color: "oklch(0.45 0 0)" }}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z" />
          </svg>
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="继续追问，例如：CE认证需要多长时间？预计费用是多少？"
            className="flex-1 bg-transparent text-sm outline-none placeholder:text-zinc-600"
            style={{ color: "oklch(0.9 0 0)" }}
            disabled={isLoading}
          />
          <button
            onClick={handleSubmit}
            disabled={!question.trim() || isLoading}
            className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-md transition-colors flex-shrink-0"
            style={{
              backgroundColor:
                question.trim() && !isLoading ? "#d4830a" : "oklch(0.18 0 0)",
              color: question.trim() && !isLoading ? "#0a0a0a" : "oklch(0.4 0 0)",
              cursor: question.trim() && !isLoading ? "pointer" : "not-allowed",
            }}
            onMouseEnter={(e) => {
              if (question.trim() && !isLoading) {
                (e.currentTarget as HTMLElement).style.backgroundColor = "#bf7509";
              }
            }}
            onMouseLeave={(e) => {
              if (question.trim() && !isLoading) {
                (e.currentTarget as HTMLElement).style.backgroundColor = "#d4830a";
              }
            }}
          >
            {isLoading ? (
              <svg className="animate-spin w-3.5 h-3.5" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
            ) : (
              <>
                发送
                <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
                </svg>
              </>
            )}
          </button>
        </div>
        <p className="text-xs mt-2 text-center" style={{ color: "oklch(0.38 0 0)" }}>
          基于上方报告追问 · Enter 发送
        </p>
      </div>
    </div>
  );
}

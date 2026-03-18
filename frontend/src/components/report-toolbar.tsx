"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { exportPdf } from "@/lib/api";

interface ReportToolbarProps {
  product: string;
  markets: string[];
  reportText: string;
  onOpenKnowledge: () => void;
}

export function ReportToolbar({
  product,
  markets,
  reportText,
  onOpenKnowledge,
}: ReportToolbarProps) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExportPdf = async () => {
    if (isExporting) return;
    setIsExporting(true);
    try {
      await exportPdf(reportText, product, markets);
    } catch {
      alert("PDF导出失败，请重试");
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div
      className="px-6 py-2.5 border-b flex items-center gap-3 flex-shrink-0"
      style={{ borderColor: "#e5e5e5", backgroundColor: "#f7f7f8" }}
    >
      {/* Product name */}
      <span className="text-sm font-medium text-zinc-700 shrink-0">{product}</span>

      {/* Market badges */}
      {markets.length > 0 && (
        <div className="flex gap-1.5 flex-wrap">
          {markets.map((m) => (
            <span
              key={m}
              className="text-[11px] px-2 py-0.5 rounded font-medium"
              style={{
                backgroundColor: "rgba(16, 163, 127, 0.1)",
                color: "#10a37f",
              }}
            >
              {m}
            </span>
          ))}
        </div>
      )}

      {/* Spacer */}
      <div className="flex-1" />

      {/* Export PDF button */}
      <Button
        size="sm"
        variant="outline"
        onClick={handleExportPdf}
        disabled={isExporting}
        className="h-7 text-xs px-3 gap-1.5 border-zinc-300 text-zinc-600 hover:text-zinc-800 hover:border-zinc-400 hover:bg-zinc-100"
      >
        {isExporting ? (
          <>
            {/* Spinner */}
            <svg
              className="w-3.5 h-3.5 animate-spin"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path
                strokeLinecap="round"
                d="M12 2a10 10 0 0 1 10 10"
                style={{ opacity: 0.3 }}
              />
              <path strokeLinecap="round" d="M12 2a10 10 0 0 1 10 10" />
            </svg>
            导出中…
          </>
        ) : (
          <>
            {/* Download icon */}
            <svg
              className="w-3.5 h-3.5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            导出 PDF
          </>
        )}
      </Button>

      {/* Knowledge drawer button */}
      <Button
        size="sm"
        variant="outline"
        onClick={onOpenKnowledge}
        className="h-7 text-xs px-3 gap-1.5 border-zinc-300 text-zinc-600 hover:text-zinc-800 hover:border-zinc-400 hover:bg-zinc-100"
      >
        {/* Book icon */}
        <svg
          className="w-3.5 h-3.5"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
        </svg>
        知识库
      </Button>
    </div>
  );
}

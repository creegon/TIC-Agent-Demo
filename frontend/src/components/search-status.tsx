"use client";

import { VizData } from "@/app/page";

export type SearchStep = {
  id: string;
  label: string;
  status: "pending" | "running" | "done" | "error";
};

interface SearchStatusProps {
  steps: SearchStep[];
  currentMessage?: string;
  vizData?: VizData;
}

const statusIcon = (status: SearchStep["status"]) => {
  switch (status) {
    case "done":
      return (
        <svg className="w-3.5 h-3.5 text-green-500 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
        </svg>
      );
    case "running":
      return (
        <svg className="w-3.5 h-3.5 flex-shrink-0 animate-spin" viewBox="0 0 24 24" fill="none" style={{ color: "#d4830a" }}>
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
        </svg>
      );
    case "error":
      return (
        <svg className="w-3.5 h-3.5 text-red-500 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      );
    default:
      return (
        <div
          className="w-3.5 h-3.5 rounded-full border flex-shrink-0"
          style={{ borderColor: "oklch(0.3 0 0)" }}
        />
      );
  }
};

export function SearchStatus({ steps, currentMessage, vizData }: SearchStatusProps) {
  if (steps.length === 0) return null;

  const hasKeywords = vizData && vizData.searchKeywords.length > 0;
  const hasSources = vizData && vizData.sources.length > 0;
  const hasFunnel = vizData?.funnelSummary;

  return (
    <div
      className="rounded-lg border p-4 mb-4"
      style={{
        backgroundColor: "oklch(0.11 0 0)",
        borderColor: "oklch(0.2 0 0)",
      }}
    >
      <p className="text-xs font-medium mb-3" style={{ color: "#d4830a" }}>
        🔍 正在检索合规信息
      </p>

      {/* Step list */}
      <div className="flex flex-col gap-2">
        {steps.map((step) => (
          <div key={step.id} className="flex items-center gap-2">
            {statusIcon(step.status)}
            <span
              className="text-xs"
              style={{
                color:
                  step.status === "running"
                    ? "oklch(0.9 0 0)"
                    : step.status === "done"
                    ? "oklch(0.65 0 0)"
                    : step.status === "error"
                    ? "#f87171"
                    : "oklch(0.45 0 0)",
              }}
            >
              {step.label}
            </span>
          </div>
        ))}
      </div>

      {/* VIZ: Search keywords */}
      {hasKeywords && (
        <div className="mt-3 pt-3 border-t" style={{ borderColor: "oklch(0.18 0 0)" }}>
          <p className="text-[10px] font-medium mb-1.5" style={{ color: "oklch(0.5 0 0)" }}>
            搜索关键词
          </p>
          <div className="flex flex-wrap gap-1.5">
            {vizData.searchKeywords.slice(0, 12).map((kw, i) => (
              <span
                key={i}
                className="text-[10px] px-2 py-0.5 rounded-full"
                style={{
                  backgroundColor: "rgba(212, 131, 10, 0.1)",
                  color: "#d4830a",
                  border: "1px solid rgba(212, 131, 10, 0.2)",
                }}
              >
                {kw}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* VIZ: Sources */}
      {hasSources && (
        <div className="mt-3 pt-3 border-t" style={{ borderColor: "oklch(0.18 0 0)" }}>
          <p className="text-[10px] font-medium mb-1.5" style={{ color: "oklch(0.5 0 0)" }}>
            已检索来源 ({vizData.sources.length})
          </p>
          <div className="flex flex-wrap gap-1.5">
            {vizData.sources.slice(0, 8).map((src, i) => {
              let host = src.url;
              try {
                host = new URL(src.url).hostname.replace("www.", "");
              } catch {
                // keep raw
              }
              const credColor =
                src.credibility === "high"
                  ? "#4ade80"
                  : src.credibility === "medium"
                  ? "#d4830a"
                  : "oklch(0.5 0 0)";

              return (
                <span
                  key={i}
                  className="text-[10px] px-2 py-0.5 rounded-full"
                  style={{
                    backgroundColor: "oklch(0.15 0 0)",
                    color: credColor,
                    border: `1px solid ${credColor}33`,
                  }}
                  title={src.url}
                >
                  {host}
                </span>
              );
            })}
            {vizData.sources.length > 8 && (
              <span
                className="text-[10px] px-2 py-0.5 rounded-full"
                style={{ backgroundColor: "oklch(0.15 0 0)", color: "oklch(0.45 0 0)" }}
              >
                +{vizData.sources.length - 8} 更多
              </span>
            )}
          </div>
        </div>
      )}

      {/* VIZ: Funnel summary */}
      {hasFunnel && (
        <div className="mt-3 pt-3 border-t" style={{ borderColor: "oklch(0.18 0 0)" }}>
          <p className="text-[10px] font-medium mb-2" style={{ color: "oklch(0.5 0 0)" }}>
            信息漏斗
          </p>
          <div className="flex items-center gap-2 text-[10px]" style={{ color: "oklch(0.55 0 0)" }}>
            <span className="text-zinc-400">{hasFunnel.total_searched} 搜索</span>
            <span>→</span>
            <span className="text-zinc-400">{hasFunnel.passed_relevance} 相关</span>
            <span>→</span>
            <span className="text-zinc-400">{hasFunnel.passed_credibility} 可信</span>
            <span>→</span>
            <span style={{ color: "#d4830a" }}>{hasFunnel.used_in_report} 采用</span>
          </div>
        </div>
      )}

      {/* Current message */}
      {currentMessage && (
        <p
          className="text-xs mt-3 pt-3 border-t"
          style={{
            borderColor: "oklch(0.18 0 0)",
            color: "oklch(0.55 0 0)",
          }}
        >
          {currentMessage}
        </p>
      )}
    </div>
  );
}

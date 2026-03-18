"use client";

import { useState } from "react";
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
  /** When true, renders as a collapsible "research log" (post-analysis) */
  isLog?: boolean;
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
        <svg className="w-3.5 h-3.5 flex-shrink-0 animate-spin" viewBox="0 0 24 24" fill="none" style={{ color: "#10a37f" }}>
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
          style={{ borderColor: "#e5e5e5" }}
        />
      );
  }
};

/** Domain credibility classification */
function classifyDomain(hostname: string): { label: string; color: string } {
  const h = hostname.toLowerCase();
  const officialTLDs = [".gov", ".eu", ".int"];
  const standardBodies = ["iec.ch", "iso.org", "etsi.org", "ansi.org", "nist.gov", "fcc.gov", "sac.gov.cn", "cqc.com.cn", "ul.com", "tuvsud.com", "bureau-veritas.com", "intertek.com", "sgs.com", "dnv.com", "tüv"];
  const ticBodies = ["ul.com", "tuvsud.com", "bureau-veritas.com", "intertek.com", "sgs.com", "dnv.com", "dekra.com", "cts.com", "element.com"];

  if (officialTLDs.some((t) => h.endsWith(t)) || h.includes(".gov.")) {
    return { label: "官方", color: "#16a34a" };
  }
  if (standardBodies.some((s) => h.includes(s))) {
    return { label: "标准", color: "#2563eb" };
  }
  if (ticBodies.some((s) => h.includes(s))) {
    return { label: "TIC机构", color: "#10a37f" };
  }
  return { label: "参考", color: "#6e6e80" };
}

export function SearchStatus({ steps, currentMessage, vizData, isLog = false }: SearchStatusProps) {
  const [collapsed, setCollapsed] = useState(false);

  if (steps.length === 0 && !isLog) return null;

  const hasKeywords = vizData && vizData.searchKeywords.length > 0;
  const hasSources = vizData && vizData.sources.length > 0;
  const hasFunnel = vizData?.funnelSummary;

  if (isLog && !hasKeywords && !hasSources) return null;

  return (
    <div
      className="rounded-lg border mb-4"
      style={{
        backgroundColor: isLog ? "#fafafa" : "#f7f7f8",
        borderColor: isLog ? "#d4d4d4" : "#e5e5e5",
      }}
    >
      {/* Header — clickable when it's a log */}
      <div
        className={`flex items-center gap-2 px-4 py-3 ${isLog ? "cursor-pointer select-none" : ""}`}
        onClick={isLog ? () => setCollapsed((v) => !v) : undefined}
      >
        <p className="text-xs font-medium flex-1" style={{ color: isLog ? "#6e6e80" : "#10a37f" }}>
          {isLog ? "📋 调研日志" : "🔍 正在检索合规信息"}
        </p>
        {hasFunnel && isLog && (
          <span className="text-[10px] text-zinc-400">
            {hasFunnel.total_searched} 搜索 → {hasFunnel.used_in_report} 采用
          </span>
        )}
        {isLog && (
          <svg
            className={`w-3.5 h-3.5 transition-transform flex-shrink-0`}
            style={{ color: "#9ca3af", transform: collapsed ? "rotate(-90deg)" : "rotate(0deg)" }}
            viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        )}
      </div>

      {/* Body — hidden when collapsed */}
      {!collapsed && (
        <div className="px-4 pb-4">
          {/* Step list — only shown during live search */}
          {!isLog && steps.length > 0 && (
            <div className="flex flex-col gap-2 mb-3">
              {steps.map((step) => (
                <div key={step.id} className="flex items-center gap-2">
                  {statusIcon(step.status)}
                  <span
                    className="text-xs"
                    style={{
                      color:
                        step.status === "running"
                          ? "#0d0d0d"
                          : step.status === "done"
                          ? "#6e6e80"
                          : step.status === "error"
                          ? "#ef4444"
                          : "#9ca3af",
                    }}
                  >
                    {step.label}
                  </span>
                </div>
              ))}
            </div>
          )}

          {/* VIZ: Search keywords */}
          {hasKeywords && (
            <div className={isLog ? "" : "mt-3 pt-3 border-t"} style={{ borderColor: "#e5e5e5" }}>
              <p className="text-[10px] font-medium mb-1.5" style={{ color: "#6e6e80" }}>
                搜索关键词 ({vizData.searchKeywords.length})
              </p>
              <div className="flex flex-wrap gap-1.5">
                {vizData.searchKeywords.slice(0, 16).map((kw, i) => (
                  <span
                    key={i}
                    className="text-[10px] px-2 py-0.5 rounded-full"
                    style={{
                      backgroundColor: "rgba(16, 163, 127, 0.08)",
                      color: "#10a37f",
                      border: "1px solid rgba(16, 163, 127, 0.2)",
                    }}
                  >
                    {kw}
                  </span>
                ))}
                {vizData.searchKeywords.length > 16 && (
                  <span className="text-[10px] px-2 py-0.5 rounded-full" style={{ color: "#9ca3af" }}>
                    +{vizData.searchKeywords.length - 16} 更多
                  </span>
                )}
              </div>
            </div>
          )}

          {/* VIZ: Sources */}
          {hasSources && (
            <div className="mt-3 pt-3 border-t" style={{ borderColor: "#e5e5e5" }}>
              <p className="text-[10px] font-medium mb-1.5" style={{ color: "#6e6e80" }}>
                已检索来源 ({vizData.sources.length})
              </p>
              <div className="flex flex-wrap gap-1.5">
                {vizData.sources.slice(0, 12).map((src, i) => {
                  let host = src.url;
                  try {
                    host = new URL(src.url).hostname.replace("www.", "");
                  } catch {
                    // keep raw
                  }
                  const { label, color } = classifyDomain(host);

                  return (
                    <span
                      key={i}
                      className="text-[10px] px-2 py-0.5 rounded-full flex items-center gap-1"
                      style={{
                        backgroundColor: "#f7f7f8",
                        color: "#6e6e80",
                        border: `1px solid #e5e5e5`,
                      }}
                      title={src.url}
                    >
                      <span style={{ color }}>{host}</span>
                      <span
                        className="text-[9px] px-1 rounded"
                        style={{ backgroundColor: `${color}18`, color }}
                      >
                        {label}
                      </span>
                    </span>
                  );
                })}
                {vizData.sources.length > 12 && (
                  <span
                    className="text-[10px] px-2 py-0.5 rounded-full"
                    style={{ backgroundColor: "#f7f7f8", color: "#6e6e80" }}
                  >
                    +{vizData.sources.length - 12} 更多
                  </span>
                )}
              </div>
            </div>
          )}

          {/* VIZ: Funnel summary — only in live mode */}
          {hasFunnel && !isLog && (
            <div className="mt-3 pt-3 border-t" style={{ borderColor: "#e5e5e5" }}>
              <p className="text-[10px] font-medium mb-2" style={{ color: "#6e6e80" }}>
                信息漏斗
              </p>
              <div className="flex items-center gap-2 text-[10px]" style={{ color: "#6e6e80" }}>
                <span className="text-zinc-600">{hasFunnel.total_searched} 搜索</span>
                <span>→</span>
                <span className="text-zinc-600">{hasFunnel.passed_relevance} 相关</span>
                <span>→</span>
                <span className="text-zinc-600">{hasFunnel.passed_credibility} 可信</span>
                <span>→</span>
                <span style={{ color: "#10a37f" }}>{hasFunnel.used_in_report} 采用</span>
              </div>
            </div>
          )}

          {/* Current message — only in live mode */}
          {!isLog && currentMessage && (
            <p
              className="text-xs mt-3 pt-3 border-t"
              style={{ borderColor: "#e5e5e5", color: "#6e6e80" }}
            >
              {currentMessage}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

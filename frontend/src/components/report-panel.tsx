"use client";

import { useState, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { SearchStatus, SearchStep } from "@/components/search-status";
import { VizData } from "@/app/page";
import { ChartTabs } from "@/components/charts/chart-tabs";
import { ReportToolbar } from "@/components/report-toolbar";
import { KnowledgeDrawer } from "@/components/knowledge-drawer";

interface ReportPanelProps {
  report: string | null;
  isLoading: boolean;
  searchSteps: SearchStep[];
  currentSearchMessage?: string;
  product?: string;
  markets?: string[];
  vizData?: VizData;
  errorMessage?: string | null;
  /** Called when user submits a followup; receives the question and a fn to stream-append text */
  onFollowup?: (question: string, appendToReport: (section: string) => void) => void;
  isFollowupLoading?: boolean;
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full py-16 text-center px-4">
      {/* Icon */}
      <div
        className="w-20 h-20 rounded-2xl flex items-center justify-center mb-6 border"
        style={{
          backgroundColor: "oklch(0.11 0 0)",
          borderColor: "oklch(0.2 0 0)",
        }}
      >
        <svg
          className="w-9 h-9"
          style={{ color: "rgba(212,131,10,0.6)" }}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25zM6.75 12h.008v.008H6.75V12zm0 3h.008v.008H6.75V15zm0 3h.008v.008H6.75V18z" />
        </svg>
      </div>

      <h3 className="text-base font-semibold text-zinc-300 mb-2">
        选择产品和市场，开始合规检查
      </h3>
      <p className="text-sm max-w-sm leading-relaxed mb-8" style={{ color: "oklch(0.48 0 0)" }}>
        描述您的产品，选择目标销售市场，AI 将自动检索适用法规标准并生成结构化合规报告
      </p>

      {/* Steps */}
      <div className="flex flex-col gap-3 w-full max-w-xs text-left mb-8">
        {[
          { step: "1", text: "填写产品描述（越详细越准确）" },
          { step: "2", text: "选择目标市场（EU / US / CN 等）" },
          { step: "3", text: "点击「生成合规报告」，等待 AI 分析" },
        ].map(({ step, text }) => (
          <div key={step} className="flex items-start gap-3">
            <div
              className="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold flex-shrink-0 mt-0.5"
              style={{ backgroundColor: "rgba(212,131,10,0.15)", color: "#d4830a" }}
            >
              {step}
            </div>
            <span className="text-xs leading-relaxed" style={{ color: "oklch(0.55 0 0)" }}>
              {text}
            </span>
          </div>
        ))}
      </div>

      {/* Cert badges */}
      <div
        className="flex flex-wrap justify-center gap-2 text-xs"
        style={{ color: "oklch(0.4 0 0)" }}
      >
        {["CE 认证", "FCC 认证", "CCC 认证", "REACH", "RoHS", "PSE"].map((cert) => (
          <span
            key={cert}
            className="px-2.5 py-1 rounded-full border text-[11px]"
            style={{ borderColor: "oklch(0.2 0 0)", backgroundColor: "oklch(0.11 0 0)" }}
          >
            {cert}
          </span>
        ))}
      </div>
    </div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-full py-16 text-center px-4">
      <div
        className="w-16 h-16 rounded-2xl flex items-center justify-center mb-5 border"
        style={{ backgroundColor: "rgba(239,68,68,0.08)", borderColor: "rgba(239,68,68,0.25)" }}
      >
        <svg className="w-7 h-7 text-red-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
        </svg>
      </div>
      <h3 className="text-sm font-semibold text-red-400 mb-2">
        后端连接失败
      </h3>
      <p className="text-xs max-w-xs leading-relaxed mb-4" style={{ color: "oklch(0.5 0 0)" }}>
        {message.includes("fetch") || message.includes("network") || message.includes("Failed")
          ? "无法连接到后端服务，请确认后端已启动（uvicorn backend.main:app --port 8000）"
          : message}
      </p>
      <p className="text-[11px]" style={{ color: "oklch(0.4 0 0)" }}>
        本地开发：后端运行在 <code className="px-1 py-0.5 rounded" style={{ backgroundColor: "oklch(0.15 0 0)", color: "#d4830a" }}>localhost:8000</code>
      </p>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Markdown renderer using react-markdown + remark-gfm
// ─────────────────────────────────────────────────────────────

function ReportMarkdown({ content }: { content: string }) {
  return (
    <div className="prose prose-invert max-w-none text-sm leading-relaxed report-markdown">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Headings
          h1: ({ children }) => (
            <h1 className="text-xl font-bold text-zinc-100 mb-4 mt-6 first:mt-0">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2
              className="text-base font-semibold mb-3 mt-6 pb-2 border-b"
              style={{ color: "#d4830a", borderColor: "oklch(0.18 0 0)" }}
            >
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-sm font-semibold text-zinc-300 mb-2 mt-4">
              {children}
            </h3>
          ),
          h4: ({ children }) => (
            <h4 className="text-sm font-medium text-zinc-400 mb-2 mt-3">
              {children}
            </h4>
          ),

          // Paragraph
          p: ({ children }) => (
            <p className="text-zinc-400 mb-3 leading-relaxed">
              {children}
            </p>
          ),

          // Lists
          ul: ({ children }) => (
            <ul className="list-disc list-outside ml-5 mb-3 space-y-1 text-zinc-400">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal list-outside ml-5 mb-3 space-y-1 text-zinc-400">
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li className="text-zinc-400 leading-relaxed">
              {children}
            </li>
          ),

          // Blockquote
          blockquote: ({ children }) => (
            <blockquote
              className="border-l-2 pl-4 py-1 my-3 text-xs italic"
              style={{
                borderColor: "#d4830a",
                color: "oklch(0.6 0 0)",
                backgroundColor: "rgba(212, 131, 10, 0.04)",
              }}
            >
              {children}
            </blockquote>
          ),

          // Horizontal rule
          hr: () => (
            <hr
              className="my-5 border-0 border-t"
              style={{ borderColor: "oklch(0.2 0 0)" }}
            />
          ),

          // Inline code
          code: ({ className, children, ...rest }) => {
            const isBlock = className?.includes("language-");
            if (isBlock) {
              return (
                <code
                  className={`block rounded-md px-4 py-3 my-3 text-xs font-mono overflow-x-auto ${className ?? ""}`}
                  style={{
                    backgroundColor: "oklch(0.13 0 0)",
                    color: "#e5c07b",
                    border: "1px solid oklch(0.2 0 0)",
                  }}
                  {...rest}
                >
                  {children}
                </code>
              );
            }
            return (
              <code
                className="rounded px-1.5 py-0.5 text-[11px] font-mono"
                style={{
                  backgroundColor: "oklch(0.15 0 0)",
                  color: "#e5c07b",
                }}
                {...rest}
              >
                {children}
              </code>
            );
          },

          // Pre wrapper (for code blocks)
          pre: ({ children }) => (
            <pre
              className="rounded-md my-3 overflow-x-auto"
              style={{
                backgroundColor: "oklch(0.13 0 0)",
                border: "1px solid oklch(0.2 0 0)",
              }}
            >
              {children}
            </pre>
          ),

          // Links — amber color
          a: ({ href, children }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="underline underline-offset-2 transition-colors"
              style={{ color: "#d4830a" }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLAnchorElement).style.color = "#f59e0b";
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLAnchorElement).style.color = "#d4830a";
              }}
            >
              {children}
            </a>
          ),

          // Bold / strong
          strong: ({ children }) => (
            <strong className="font-semibold text-zinc-200">{children}</strong>
          ),

          // Italic / em
          em: ({ children }) => (
            <em className="italic text-zinc-300">{children}</em>
          ),

          // ── Tables (remark-gfm) ──────────────────────────────────
          table: ({ children }) => (
            <div className="overflow-x-auto my-4 rounded-lg border" style={{ borderColor: "oklch(0.22 0 0)" }}>
              <table className="w-full text-xs border-collapse">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead style={{ backgroundColor: "oklch(0.15 0 0)" }}>
              {children}
            </thead>
          ),
          tbody: ({ children }) => (
            <tbody>{children}</tbody>
          ),
          tr: ({ children }) => (
            <tr
              className="border-t transition-colors"
              style={{ borderColor: "oklch(0.18 0 0)" }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLTableRowElement).style.backgroundColor = "oklch(0.13 0 0)";
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLTableRowElement).style.backgroundColor = "";
              }}
            >
              {children}
            </tr>
          ),
          th: ({ children }) => (
            <th
              className="px-3 py-2 text-left font-semibold"
              style={{ color: "#d4830a" }}
            >
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-3 py-2 text-zinc-400">
              {children}
            </td>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// ReportPanel (main export)
// ─────────────────────────────────────────────────────────────

export function ReportPanel({
  report,
  isLoading,
  searchSteps,
  currentSearchMessage,
  product,
  markets,
  vizData,
  errorMessage,
}: ReportPanelProps) {
  const [knowledgeOpen, setKnowledgeOpen] = useState(false);

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Toolbar — only shown when report exists */}
      {report && !isLoading && product && (
        <ReportToolbar
          product={product}
          markets={markets ?? []}
          reportText={report}
          onOpenKnowledge={() => setKnowledgeOpen(true)}
        />
      )}

      {/* Header strip during loading */}
      {isLoading && (product || markets) && (
        <div
          className="px-6 py-3 border-b flex items-center gap-3 flex-shrink-0"
          style={{ borderColor: "oklch(0.16 0 0)" }}
        >
          <span className="text-sm font-medium text-zinc-300">{product}</span>
          {markets && markets.length > 0 && (
            <div className="flex gap-1.5">
              {markets.map((m) => (
                <span
                  key={m}
                  className="text-[11px] px-2 py-0.5 rounded font-medium"
                  style={{
                    backgroundColor: "rgba(212, 131, 10, 0.12)",
                    color: "#d4830a",
                  }}
                >
                  {m}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Knowledge drawer */}
      <KnowledgeDrawer
        open={knowledgeOpen}
        onClose={() => setKnowledgeOpen(false)}
        product={product ?? ""}
        markets={markets ?? []}
      />

      <div className="flex-1 overflow-y-auto px-6 py-5">
        {/* Loading / search status */}
        {isLoading && (
          <SearchStatus
            steps={searchSteps}
            currentMessage={currentSearchMessage}
            vizData={vizData}
          />
        )}

        {/* Empty state or error state */}
        {!report && !isLoading && !errorMessage && <EmptyState />}
        {!report && !isLoading && errorMessage && <ErrorState message={errorMessage} />}

        {/* Report content */}
        {report && !isLoading && (
          <Tabs defaultValue="report" className="w-full">
            <TabsList
              className="mb-5 h-8"
              style={{
                backgroundColor: "oklch(0.13 0 0)",
                border: "1px solid oklch(0.2 0 0)",
              }}
            >
              <TabsTrigger
                value="report"
                className="text-xs h-6 px-3 data-[state=active]:text-zinc-100"
                style={{ color: "oklch(0.55 0 0)" }}
              >
                📋 合规报告
              </TabsTrigger>
              <TabsTrigger
                value="charts"
                className="text-xs h-6 px-3 data-[state=active]:text-zinc-100"
                style={{ color: "oklch(0.55 0 0)" }}
              >
                📊 图表视图
              </TabsTrigger>
              <TabsTrigger
                value="checklist"
                className="text-xs h-6 px-3 data-[state=active]:text-zinc-100"
                style={{ color: "oklch(0.55 0 0)" }}
              >
                ✅ 核查清单
              </TabsTrigger>
            </TabsList>

            <TabsContent value="report">
              <ReportMarkdown content={report} />
              <ChartTabs reportText={report} markets={markets ?? []} />
            </TabsContent>

            <TabsContent value="charts">
              <ChartTabs reportText={report} markets={markets ?? []} />
            </TabsContent>

            <TabsContent value="checklist">
              <div
                className="rounded-lg border p-8 text-center"
                style={{
                  backgroundColor: "oklch(0.11 0 0)",
                  borderColor: "oklch(0.2 0 0)",
                }}
              >
                <p className="text-sm" style={{ color: "oklch(0.5 0 0)" }}>
                  ✅ 交互式核查清单（即将推出）
                </p>
              </div>
            </TabsContent>
          </Tabs>
        )}

        {/* Show report while streaming (typewriter effect) */}
        {report && isLoading && (
          <div className="mt-4">
            <ReportMarkdown content={report} />
          </div>
        )}
      </div>
    </div>
  );
}

"use client";

import { useState, useRef } from "react";
import { Navbar } from "@/components/navbar";
import { InputPanel } from "@/components/input-panel";
import { ReportPanel } from "@/components/report-panel";
import { FollowupBar } from "@/components/followup-bar";
import { SearchStep } from "@/components/search-status";
import { analyzeProduct, followUp, type ChartsData } from "@/lib/api";

interface SubmitData {
  product: string;
  markets: string[];
  extraInfo: string;
}

// VIZ data accumulated from SSE viz events
export interface VizData {
  searchKeywords: string[];
  sources: Array<{ url: string; credibility?: string }>;
  funnelSummary?: {
    total_searched: number;
    passed_relevance: number;
    passed_credibility: number;
    used_in_report: number;
  };
}

export default function Home() {
  const [report, setReport] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isFollowupLoading, setIsFollowupLoading] = useState(false);
  const [searchSteps, setSearchSteps] = useState<SearchStep[]>([]);
  const [currentSearchMessage, setCurrentSearchMessage] = useState<string>("");
  const [currentProduct, setCurrentProduct] = useState<string>("");
  const [currentMarkets, setCurrentMarkets] = useState<string[]>([]);
  const [vizData, setVizData] = useState<VizData>({ searchKeywords: [], sources: [] });
  const [chartsData, setChartsData] = useState<ChartsData | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  // Mobile: whether the input panel is expanded
  const [mobileInputOpen, setMobileInputOpen] = useState(false);
  // Research log — persists after analysis completes
  const [researchLog, setResearchLog] = useState<{ vizData: VizData; steps: SearchStep[] } | null>(null);

  // followup conversation history (messages array sent to backend)
  const messagesRef = useRef<Array<{ role: string; content: string }>>([]);

  // accumulated report text (for followup sections)
  const reportRef = useRef<string>("");

  // Track vizData in a ref for access from async callbacks
  const vizDataRef = useRef<VizData>({ searchKeywords: [], sources: [] });

  const handleSubmit = async (data: SubmitData) => {
    setIsLoading(true);
    setReport(null);
    setErrorMessage(null);
    setCurrentProduct(data.product);
    setCurrentMarkets(data.markets);
    setVizData({ searchKeywords: [], sources: [] });
    vizDataRef.current = { searchKeywords: [], sources: [] };
    setChartsData(null);
    setResearchLog(null);
    messagesRef.current = [];
    reportRef.current = "";
    // Collapse input panel on mobile after submit
    setMobileInputOpen(false);

    // Add a single "searching" step — we'll update label from SSE status events
    setSearchSteps([{ id: "live", label: "连接后端...", status: "running" }]);
    setCurrentSearchMessage(`正在分析 ${data.product} 在 ${data.markets.join(", ")} 市场的合规要求...`);

    let accumulatedReport = "";

    await analyzeProduct(
      { product: data.product, markets: data.markets, extra_info: data.extraInfo },
      {
        onStatus: (text) => {
          setSearchSteps([{ id: "live", label: text.trim(), status: "running" }]);
          setCurrentSearchMessage(text.trim());
        },

        onViz: (raw) => {
          const vizPayload = raw as Record<string, unknown>;
          setVizData((prev) => {
            const next = { ...prev };

            if (vizPayload.type === "search_start") {
              const keywords = vizPayload.keywords;
              if (Array.isArray(keywords)) {
                next.searchKeywords = [...new Set([...prev.searchKeywords, ...keywords as string[]])];
              }
            }

            if (vizPayload.type === "search_results") {
              const results = vizPayload.results;
              if (Array.isArray(results)) {
                const newSources = (results as Array<{ url: string; credibility?: string }>).map((r) => ({
                  url: r.url,
                  credibility: r.credibility,
                }));
                next.sources = [...prev.sources, ...newSources];
              }
            }

            if (vizPayload.type === "funnel_summary") {
              next.funnelSummary = vizPayload as unknown as VizData["funnelSummary"];
            }

            // Keep ref in sync for use in onDone callback
            vizDataRef.current = next;
            return next;
          });
        },

        onChunk: (text) => {
          accumulatedReport += text;
          // Stream report in real time for typewriter effect
          setReport(accumulatedReport);
        },

        onDone: (fullReport, charts) => {
          // Backend sends the full report text on done; prefer it if non-empty
          const finalReport = fullReport.trim() ? fullReport : accumulatedReport;
          reportRef.current = finalReport;
          setReport(finalReport);

          // Save charts data from backend
          if (charts) {
            setChartsData(charts);
          }

          // Build initial messages array for followup context
          messagesRef.current = [
            {
              role: "user",
              content: `请分析 ${data.product} 在 ${data.markets.join(", ")} 市场的合规要求。${data.extraInfo ? "\n额外信息：" + data.extraInfo : ""}`,
            },
            { role: "assistant", content: finalReport },
          ];

          setIsLoading(false);
          // Save research log using the ref (avoids nested setState)
          setResearchLog({ vizData: vizDataRef.current, steps: [{ id: "done", label: "分析完成", status: "done" }] });
          setSearchSteps([{ id: "live", label: "分析完成", status: "done" }]);
          setCurrentSearchMessage("");

          // Clear live steps after short delay (research log persists separately)
          setTimeout(() => {
            setSearchSteps([]);
          }, 800);
        },

        onError: (msg) => {
          setSearchSteps([{ id: "live", label: `错误: ${msg}`, status: "error" }]);
          setCurrentSearchMessage("");
          setErrorMessage(msg);
          setIsLoading(false);
        },
      },
    );
  };

  const handleFollowup = async (question: string, appendToReport: (section: string) => void) => {
    setIsFollowupLoading(true);

    // Add user question to messages
    messagesRef.current = [...messagesRef.current, { role: "user", content: question }];

    let answerBuffer = "";

    // Separator will be appended first
    appendToReport(`\n\n---\n\n**追问：${question}**\n\n`);

    await followUp(
      messagesRef.current.slice(0, -1), // history without the current question
      question,
      {
        onChunk: (text) => {
          answerBuffer += text;
          appendToReport(text);
        },
        onDone: () => {
          // Add assistant answer to messages for next followup
          messagesRef.current = [
            ...messagesRef.current,
            { role: "assistant", content: answerBuffer },
          ];
          setIsFollowupLoading(false);
        },
        onError: (msg) => {
          appendToReport(`\n\n> ⚠️ 追问失败：${msg}`);
          setIsFollowupLoading(false);
        },
      },
    );
  };

  return (
    <div
      className="flex flex-col"
      style={{ height: "100dvh", backgroundColor: "#ffffff" }}
    >
      {/* Top navbar */}
      <Navbar />

      {/* Mobile: collapsible input panel toggle button */}
      <div
        className="md:hidden border-b flex-shrink-0"
        style={{ borderColor: "#e5e5e5", backgroundColor: "#f7f7f8" }}
      >
        <button
          className="w-full flex items-center justify-between px-4 py-3 text-sm font-medium text-zinc-700"
          onClick={() => setMobileInputOpen((v) => !v)}
        >
          <span className="flex items-center gap-2">
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 3c.132 0 .263 0 .393 0a7.5 7.5 0 0 0 7.92 12.446A9 9 0 1 1 8.349 4.182c.101-.022.203-.04.306-.058.102-.018.205-.033.308-.045.103-.012.206-.02.31-.025.103-.004.207-.007.31-.007z" />
            </svg>
            {currentProduct ? `检查：${currentProduct.slice(0, 20)}${currentProduct.length > 20 ? "…" : ""}` : "产品 & 市场设置"}
          </span>
          <svg
            className={`w-4 h-4 transition-transform ${mobileInputOpen ? "rotate-180" : ""}`}
            viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {/* Collapsible input panel on mobile */}
        {mobileInputOpen && (
          <div className="border-t" style={{ borderColor: "#e5e5e5" }}>
            <InputPanel onSubmit={handleSubmit} isLoading={isLoading} />
          </div>
        )}
      </div>

      {/* Main content: left panel + right report */}
      <div className="flex flex-1 overflow-hidden">
        {/* Desktop: sidebar input panel */}
        <div className="hidden md:flex">
          <InputPanel onSubmit={handleSubmit} isLoading={isLoading} />
        </div>

        {/* Report panel — full width on mobile */}
        <ReportPanel
          report={report}
          isLoading={isLoading}
          searchSteps={searchSteps}
          currentSearchMessage={currentSearchMessage}
          product={currentProduct}
          markets={currentMarkets}
          vizData={vizData}
          chartsData={chartsData}
          researchLog={researchLog}
          onFollowup={handleFollowup}
          isFollowupLoading={isFollowupLoading}
          errorMessage={errorMessage}
        />
      </div>

      {/* Bottom followup bar — only visible when report is ready */}
      <FollowupBar
        visible={!!report && !isLoading}
        onSubmit={handleFollowup}
        isLoading={isFollowupLoading}
      />
    </div>
  );
}

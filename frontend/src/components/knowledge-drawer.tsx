"use client";

import { useEffect, useState } from "react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { fetchKnowledge, type KnowledgeResponse, type Regulation } from "@/lib/api";

interface KnowledgeDrawerProps {
  open: boolean;
  onClose: () => void;
  product: string;
  markets: string[];
}

function RegulationCard({ reg }: { reg: Regulation }) {
  return (
    <AccordionItem
      value={reg.standard_no}
      className="border-b last:border-0"
      style={{ borderColor: "#e5e5e5" }}
    >
      <AccordionTrigger className="py-3 px-1 hover:no-underline group">
        <div className="flex items-start gap-3 text-left w-full pr-2">
          {/* Standard number badge */}
          <span
            className="text-[11px] font-mono font-semibold px-2 py-0.5 rounded shrink-0 mt-0.5"
            style={{
              backgroundColor: "rgba(16, 163, 127, 0.1)",
              color: "#10a37f",
            }}
          >
            {reg.standard_no}
          </span>

          <div className="flex-1 min-w-0">
            {/* Name */}
            <p className="text-sm font-medium text-zinc-700 leading-snug">
              {reg.name}
            </p>

            {/* Markets + mandatory tag */}
            <div className="flex items-center gap-2 mt-1.5 flex-wrap">
              {reg.markets.map((m) => (
                <span
                  key={m}
                  className="text-[10px] px-1.5 py-0.5 rounded font-medium"
                  style={{
                    backgroundColor: "#f7f7f8",
                    color: "#6e6e80",
                    border: "1px solid #e5e5e5",
                  }}
                >
                  {m}
                </span>
              ))}
              <span
                className="text-[10px] px-1.5 py-0.5 rounded font-medium"
                style={
                  reg.mandatory
                    ? { backgroundColor: "rgba(239, 68, 68, 0.08)", color: "#ef4444" }
                    : { backgroundColor: "rgba(22, 163, 74, 0.08)", color: "#16a34a" }
                }
              >
                {reg.mandatory ? "强制" : "自愿"}
              </span>
            </div>
          </div>
        </div>
      </AccordionTrigger>

      <AccordionContent className="px-1 pb-3">
        <div
          className="rounded-lg p-3 space-y-3"
          style={{
            backgroundColor: "#f7f7f8",
            border: "1px solid #e5e5e5",
          }}
        >
          {/* Description */}
          {reg.description && (
            <div>
              <p className="text-[11px] font-semibold text-zinc-500 uppercase tracking-wider mb-1">
                描述
              </p>
              <p className="text-xs text-zinc-600 leading-relaxed">
                {reg.description}
              </p>
            </div>
          )}

          {/* Key tests */}
          {reg.key_tests && reg.key_tests.length > 0 && (
            <div>
              <p className="text-[11px] font-semibold text-zinc-500 uppercase tracking-wider mb-1.5">
                关键测试项
              </p>
              <ul className="space-y-1">
                {reg.key_tests.map((test, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-zinc-600">
                    <span
                      className="w-1.5 h-1.5 rounded-full mt-1.5 shrink-0"
                      style={{ backgroundColor: "#10a37f" }}
                    />
                    {test}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </AccordionContent>
    </AccordionItem>
  );
}

export function KnowledgeDrawer({
  open,
  onClose,
  product,
  markets,
}: KnowledgeDrawerProps) {
  const [data, setData] = useState<KnowledgeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open || !product) return;

    setLoading(true);
    setError(null);
    setData(null);

    fetchKnowledge(product, markets)
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err: unknown) => {
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg);
        setLoading(false);
      });
  }, [open, product, markets]);

  return (
    <Sheet open={open} onOpenChange={(v) => { if (!v) onClose(); }}>
      <SheetContent
        side="right"
        className="w-[420px] sm:w-[480px] flex flex-col p-0 border-l"
        style={{
          backgroundColor: "#ffffff",
          borderColor: "#e5e5e5",
        }}
      >
        {/* Header */}
        <SheetHeader
          className="px-5 py-4 border-b flex-shrink-0"
          style={{ borderColor: "#e5e5e5" }}
        >
          <div className="flex items-center gap-3">
            {/* Book icon */}
            <div
              className="w-7 h-7 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: "rgba(16, 163, 127, 0.1)" }}
            >
              <svg
                className="w-4 h-4"
                style={{ color: "#10a37f" }}
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
            </div>
            <div>
              <SheetTitle className="text-sm font-semibold text-zinc-800">
                知识库
              </SheetTitle>
              <p className="text-[11px] text-zinc-500 mt-0.5">
                {product} · {markets.join(", ")}
              </p>
            </div>
          </div>
        </SheetHeader>

        {/* Body */}
        <div className="flex-1 overflow-y-auto px-5 py-4">
          {/* Loading */}
          {loading && (
            <div className="flex flex-col items-center justify-center py-16 gap-3">
              <svg
                className="w-6 h-6 animate-spin"
                style={{ color: "#10a37f" }}
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path
                  strokeLinecap="round"
                  d="M12 2a10 10 0 0 1 10 10"
                  style={{ opacity: 0.25 }}
                />
                <path strokeLinecap="round" d="M12 2a10 10 0 0 1 10 10" />
              </svg>
              <p className="text-xs text-zinc-500">加载知识库...</p>
            </div>
          )}

          {/* Error */}
          {error && !loading && (
            <div
              className="rounded-lg p-4 text-center"
              style={{
                backgroundColor: "rgba(239, 68, 68, 0.06)",
                border: "1px solid rgba(239, 68, 68, 0.2)",
              }}
            >
              <p className="text-xs text-red-500">⚠️ {error}</p>
            </div>
          )}

          {/* Content */}
          {data && !loading && (
            <div className="space-y-4">
              {/* Category badge */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-zinc-500">产品类别：</span>
                <span
                  className="text-xs font-medium px-2.5 py-1 rounded-full"
                  style={{
                    backgroundColor: "rgba(16, 163, 127, 0.1)",
                    color: "#10a37f",
                    border: "1px solid rgba(16, 163, 127, 0.2)",
                  }}
                >
                  {data.category}
                </span>
              </div>

              {/* Divider */}
              <div
                className="border-t"
                style={{ borderColor: "#e5e5e5" }}
              />

              {/* Regulation count */}
              <p className="text-[11px] text-zinc-500">
                共 {data.regulations.length} 条相关法规
              </p>

              {/* Regulations accordion */}
              {data.regulations.length > 0 ? (
                <Accordion className="w-full">
                  {data.regulations.map((reg) => (
                    <RegulationCard key={reg.standard_no} reg={reg} />
                  ))}
                </Accordion>
              ) : (
                <div className="text-center py-8">
                  <p className="text-xs text-zinc-500">暂无相关法规数据</p>
                </div>
              )}
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}

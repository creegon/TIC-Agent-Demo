"use client";

/**
 * CostComparison — Fee breakdown chart from report data
 *
 * Key fixes from critic review:
 * - NO hardcoded $ symbol — detect currency from data/source
 * - Handle "isTotal" flag when backend can't break down fees
 * - Small amounts don't show "$0k"
 */

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { type CostData } from "@/lib/api";

// Extended type for backend data that may include isTotal flag
interface CostEntry extends CostData {
  totalFee?: number;
  isTotal?: boolean;
  source?: string;
}

interface Props {
  markets: string[];
  costData?: CostEntry[] | null;
}

// ── Currency detection ──────────────────────────────────────

function detectCurrency(data: CostEntry[]): string {
  // Check source snippets for currency indicators
  for (const d of data) {
    const src = (d.source || "").toLowerCase();
    if (src.includes("rmb") || src.includes("cny") || src.includes("元") || src.includes("￥") || src.includes("人民币")) {
      return "¥";
    }
    if (src.includes("usd") || src.includes("$") || src.includes("美元")) {
      return "$";
    }
  }
  // Check market names — CN/JP markets likely use local currency in reports
  for (const d of data) {
    const m = d.market.toLowerCase();
    if (m.includes("中国") || m === "cn") return "¥";
    if (m.includes("日本") || m === "jp") return "¥";
  }
  return "¥"; // Default to RMB since reports are in Chinese
}

function formatFee(value: number, symbol: string): string {
  if (value === 0) return "-";
  if (value >= 10000) {
    return `${symbol}${(value / 10000).toFixed(1)}万`;
  }
  if (value >= 1000) {
    return `${symbol}${value.toLocaleString()}`;
  }
  return `${symbol}${value}`;
}

// ── Tooltip ──────────────────────────────────────────────────

interface TooltipProps {
  active?: boolean;
  payload?: Array<{ name: string; value: number; color: string; payload: CostEntry }>;
  label?: string;
}

function CustomTooltip({ active, payload, label }: TooltipProps) {
  if (!active || !payload?.length) return null;

  const entry = payload[0]?.payload;
  const symbol = detectCurrency(entry ? [entry] : []);

  if (entry?.isTotal) {
    return (
      <div
        className="rounded-lg px-3 py-2 text-xs shadow-lg border"
        style={{ backgroundColor: "#fff", borderColor: "#e5e5e5", maxWidth: 260 }}
      >
        <p className="font-semibold text-zinc-800 mb-1">{label}</p>
        <div className="flex items-center gap-2">
          <span className="text-zinc-600">总费用参考：</span>
          <span className="font-bold" style={{ color: "#10a37f" }}>
            {formatFee(entry.totalFee || 0, symbol)}
          </span>
        </div>
        <p className="mt-1 text-[10px] text-zinc-400">报告未提供费用明细拆分</p>
        {entry.source && (
          <p className="mt-1 pt-1 border-t text-[10px] text-zinc-400" style={{ borderColor: "#e5e5e5" }}>
            来源：{entry.source}
          </p>
        )}
      </div>
    );
  }

  const total = payload.reduce((sum, p) => sum + (p.value ?? 0), 0);
  return (
    <div
      className="rounded-lg px-3 py-2 text-xs shadow-lg border"
      style={{ backgroundColor: "#fff", borderColor: "#e5e5e5", maxWidth: 260 }}
    >
      <p className="font-semibold text-zinc-800 mb-2">{label}</p>
      {payload.filter(p => p.value > 0).map((p) => (
        <div key={p.name} className="flex items-center gap-2 mb-1">
          <span className="inline-block w-2 h-2 rounded-sm flex-shrink-0" style={{ backgroundColor: p.color }} />
          <span className="text-zinc-600">{p.name}：</span>
          <span className="font-medium text-zinc-800">{formatFee(p.value, symbol)}</span>
        </div>
      ))}
      {total > 0 && (
        <div className="mt-2 pt-2 border-t flex justify-between" style={{ borderColor: "#e5e5e5" }}>
          <span className="text-zinc-500">合计：</span>
          <span className="font-bold" style={{ color: "#10a37f" }}>{formatFee(total, symbol)}</span>
        </div>
      )}
      {entry?.source && (
        <p className="mt-2 pt-2 border-t text-[10px] text-zinc-400" style={{ borderColor: "#e5e5e5" }}>
          来源：{entry.source}
        </p>
      )}
    </div>
  );
}

// ── Legend ────────────────────────────────────────────────────

function CustomLegend({ hasBreakdown }: { hasBreakdown: boolean }) {
  if (!hasBreakdown) {
    return (
      <div className="flex gap-4 justify-center mt-1 text-xs">
        <div className="flex items-center gap-1.5">
          <span className="inline-block w-3 h-3 rounded-sm" style={{ backgroundColor: "#3b82f6" }} />
          <span className="text-zinc-500">总费用参考</span>
        </div>
      </div>
    );
  }
  return (
    <div className="flex gap-4 justify-center mt-1 text-xs">
      {[
        { color: "#3b82f6", label: "测试费" },
        { color: "#10a37f", label: "认证费" },
        { color: "#34d399", label: "年审费" },
      ].map((item) => (
        <div key={item.label} className="flex items-center gap-1.5">
          <span className="inline-block w-3 h-3 rounded-sm" style={{ backgroundColor: item.color }} />
          <span className="text-zinc-500">{item.label}</span>
        </div>
      ))}
    </div>
  );
}

// ── No Data State ────────────────────────────────────────────

function NoDataState() {
  return (
    <div
      className="flex flex-col items-center justify-center rounded-lg border py-10"
      style={{ backgroundColor: "#f7f7f8", borderColor: "#e5e5e5", minHeight: 200 }}
    >
      <p className="text-sm font-medium text-zinc-500 mb-1">费用数据未在报告中明确提及</p>
      <p className="text-xs text-zinc-400 text-center max-w-xs">
        无法从报告文本中提取具体费用数字。请参阅报告正文中的费用描述，或联系认证机构获取报价。
      </p>
    </div>
  );
}

// ── Main Component ───────────────────────────────────────────

export function CostComparison({ costData }: Props) {
  const data = costData && costData.length > 0 ? costData : null;

  if (!data) {
    return <NoDataState />;
  }

  const symbol = detectCurrency(data);
  const hasBreakdown = data.some(d => !d.isTotal && (d.testingFee > 0 || d.certFee > 0));

  // For isTotal entries, put totalFee into testingFee for the bar chart display
  const chartData = data.map(d => {
    if (d.isTotal) {
      return { ...d, testingFee: d.totalFee || 0, certFee: 0, annualFee: 0 };
    }
    return d;
  });

  return (
    <div className="w-full">
      <div style={{ height: 280 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }} barCategoryGap="30%">
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" vertical={false} />
            <XAxis dataKey="market" tick={{ fill: "#6e6e80", fontSize: 11 }} axisLine={{ stroke: "#e5e5e5" }} tickLine={false} />
            <YAxis
              tick={{ fill: "#9ca3af", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v: number) => {
                if (v === 0) return "0";
                if (v >= 10000) return `${symbol}${(v / 10000).toFixed(0)}万`;
                return `${symbol}${(v / 1000).toFixed(0)}k`;
              }}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(0,0,0,0.03)" }} />
            {hasBreakdown ? (
              <>
                <Bar dataKey="testingFee" stackId="a" fill="#3b82f6" name="测试费" />
                <Bar dataKey="certFee" stackId="a" fill="#10a37f" name="认证费" />
                <Bar dataKey="annualFee" stackId="a" fill="#34d399" name="年审费" radius={[3, 3, 0, 0]} />
              </>
            ) : (
              <Bar dataKey="testingFee" fill="#3b82f6" name="总费用参考" radius={[3, 3, 0, 0]} />
            )}
          </BarChart>
        </ResponsiveContainer>
      </div>
      <CustomLegend hasBreakdown={hasBreakdown} />
      <p className="text-center text-[10px] text-zinc-400 mt-2">
        费用数据提取自报告原文，为行业参考区间，实际费用以认证机构报价为准。货币单位：{symbol === "¥" ? "人民币(RMB)" : "美元(USD)"}
      </p>
    </div>
  );
}

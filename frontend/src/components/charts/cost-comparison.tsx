"use client";

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

interface Props {
  markets: string[];
  costData?: CostData[] | null;
}

interface TooltipProps {
  active?: boolean;
  payload?: Array<{ name: string; value: number; color: string }>;
  label?: string;
}

function CustomTooltip({ active, payload, label }: TooltipProps) {
  if (!active || !payload?.length) return null;
  const total = payload.reduce((sum, p) => sum + (p.value ?? 0), 0);
  return (
    <div
      className="rounded-lg px-3 py-2 text-xs shadow-lg border"
      style={{
        backgroundColor: "#ffffff",
        borderColor: "#e5e5e5",
        color: "#0d0d0d",
      }}
    >
      <p className="font-semibold text-zinc-800 mb-2">{label}</p>
      {payload.map((p) => (
        <div key={p.name} className="flex items-center gap-2 mb-1">
          <span
            className="inline-block w-2 h-2 rounded-sm"
            style={{ backgroundColor: p.color }}
          />
          <span className="text-zinc-600">{p.name}：</span>
          <span className="font-medium text-zinc-800">${p.value.toLocaleString()}</span>
        </div>
      ))}
      <div
        className="mt-2 pt-2 border-t flex justify-between"
        style={{ borderColor: "#e5e5e5" }}
      >
        <span className="text-zinc-500">合计：</span>
        <span className="font-bold" style={{ color: "#10a37f" }}>
          ${total.toLocaleString()}
        </span>
      </div>
    </div>
  );
}

function CustomLegend() {
  return (
    <div className="flex gap-4 justify-center mt-1 text-xs">
      {[
        { key: "testingFee", color: "#3b82f6", label: "测试费" },
        { key: "certFee", color: "#10a37f", label: "认证费" },
        { key: "annualFee", color: "#34d399", label: "年审费" },
      ].map((item) => (
        <div key={item.key} className="flex items-center gap-1.5">
          <span
            className="inline-block w-3 h-3 rounded-sm"
            style={{ backgroundColor: item.color }}
          />
          <span className="text-zinc-500">{item.label}</span>
        </div>
      ))}
    </div>
  );
}

function NoDataState() {
  return (
    <div
      className="flex flex-col items-center justify-center rounded-lg border py-10"
      style={{ backgroundColor: "#f7f7f8", borderColor: "#e5e5e5", minHeight: 200 }}
    >
      <p className="text-sm font-medium text-zinc-500 mb-1">暂无费用数据</p>
      <p className="text-xs text-zinc-400 text-center max-w-xs">
        报告中未找到具体的认证费用信息，无法生成成本对比图
      </p>
    </div>
  );
}

export function CostComparison({ markets, costData }: Props) {
  // Only show chart if costData is explicitly provided from backend
  // Do NOT use hardcoded fallback data
  const data = costData && costData.length > 0 ? costData : null;

  if (!data) {
    return (
      <div className="w-full">
        <NoDataState />
        <p className="text-center text-[10px] text-zinc-400 mt-2">
          * 费用数据来源于报告中提取的行业参考值
        </p>
      </div>
    );
  }

  return (
    <div className="w-full">
      <div style={{ height: 280 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
            barCategoryGap="30%"
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#e5e5e5"
              vertical={false}
            />
            <XAxis
              dataKey="market"
              tick={{ fill: "#6e6e80", fontSize: 11 }}
              axisLine={{ stroke: "#e5e5e5" }}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "#9ca3af", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(0,0,0,0.03)" }} />
            <Bar dataKey="testingFee" stackId="a" fill="#3b82f6" name="测试费" radius={[0, 0, 0, 0]} />
            <Bar dataKey="certFee" stackId="a" fill="#10a37f" name="认证费" radius={[0, 0, 0, 0]} />
            <Bar dataKey="annualFee" stackId="a" fill="#34d399" name="年审费" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <CustomLegend />
      <p className="text-center text-[10px] text-zinc-400 mt-2">
        * 数据来源：报告中提取的行业参考值（USD），实际费用因产品类别和认证机构而异
      </p>
    </div>
  );
}

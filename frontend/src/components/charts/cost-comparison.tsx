"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { getMarketCertCosts } from "@/lib/chart-data";

interface Props {
  markets: string[];
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
        backgroundColor: "#18181b",
        borderColor: "#3f3f46",
        color: "#fff",
      }}
    >
      <p className="font-semibold text-zinc-100 mb-2">{label}</p>
      {payload.map((p) => (
        <div key={p.name} className="flex items-center gap-2 mb-1">
          <span
            className="inline-block w-2 h-2 rounded-sm"
            style={{ backgroundColor: p.color }}
          />
          <span className="text-zinc-300">{p.name}：</span>
          <span className="font-medium text-white">${p.value.toLocaleString()}</span>
        </div>
      ))}
      <div
        className="mt-2 pt-2 border-t flex justify-between"
        style={{ borderColor: "#3f3f46" }}
      >
        <span className="text-zinc-400">合计：</span>
        <span className="font-bold" style={{ color: "#d4830a" }}>
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
        { key: "testingFee", color: "#1a3a5c", label: "测试费" },
        { key: "certFee", color: "#d4830a", label: "认证费" },
        { key: "annualFee", color: "#e8a838", label: "年审费" },
      ].map((item) => (
        <div key={item.key} className="flex items-center gap-1.5">
          <span
            className="inline-block w-3 h-3 rounded-sm"
            style={{ backgroundColor: item.color }}
          />
          <span className="text-zinc-400">{item.label}</span>
        </div>
      ))}
    </div>
  );
}

export function CostComparison({ markets }: Props) {
  const data = getMarketCertCosts(markets);

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
              stroke="#27272a"
              vertical={false}
            />
            <XAxis
              dataKey="market"
              tick={{ fill: "#a1a1aa", fontSize: 11 }}
              axisLine={{ stroke: "#3f3f46" }}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "#71717a", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
            {/* Reference line: $20k threshold */}
            <ReferenceLine
              y={20000}
              stroke="#52525b"
              strokeDasharray="4 4"
              label={{
                value: "$20k 参考线",
                fill: "#71717a",
                fontSize: 10,
                position: "insideTopRight",
              }}
            />
            <Bar dataKey="testingFee" stackId="a" fill="#1a3a5c" name="测试费" radius={[0, 0, 0, 0]} />
            <Bar dataKey="certFee" stackId="a" fill="#d4830a" name="认证费" radius={[0, 0, 0, 0]} />
            <Bar dataKey="annualFee" stackId="a" fill="#e8a838" name="年审费" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <CustomLegend />
      <p className="text-center text-[10px] text-zinc-600 mt-2">
        * 费用为参考估算（USD），实际费用因产品类别和认证机构而异
      </p>
    </div>
  );
}

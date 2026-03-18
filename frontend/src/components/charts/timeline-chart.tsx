"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { getMarketTimelines, TimelineData } from "@/lib/chart-data";

interface Props {
  markets: string[];
}

interface TooltipProps {
  active?: boolean;
  payload?: Array<{ payload: TimelineData & { startDisplay: number } }>;
}

function CustomTooltip({ active, payload }: TooltipProps) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div
      className="rounded-lg px-3 py-2 text-xs shadow-lg border"
      style={{
        backgroundColor: "#18181b",
        borderColor: "#3f3f46",
        color: "#fff",
      }}
    >
      <p className="font-semibold text-zinc-100 mb-1">{d.name}</p>
      <p className="text-zinc-300">
        市场：<span className="font-medium text-white">{d.market}</span>
      </p>
      <p className="text-zinc-300">
        开始：第 <span className="font-medium text-white">{d.start}</span> 周
      </p>
      <p className="text-zinc-300">
        周期：<span className="font-medium" style={{ color: "#d4830a" }}>{d.duration} 周</span>
      </p>
    </div>
  );
}

export function TimelineChart({ markets }: Props) {
  const rawData = getMarketTimelines(markets);

  // For Gantt simulation: we use two stacked bars
  // Bar 1 (transparent): start offset
  // Bar 2 (colored): duration
  const data = rawData.map((d) => ({
    ...d,
    startDisplay: d.start,    // invisible spacer
    durationDisplay: d.duration, // visible bar
  }));

  // Limit to reasonable number of rows
  const displayData = data.slice(0, 12);

  // Calculate total weeks for X axis
  const maxWeeks = Math.max(...displayData.map((d) => d.start + d.duration), 16);

  return (
    <div className="w-full">
      <div style={{ height: Math.max(200, displayData.length * 32 + 40) }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            layout="vertical"
            data={displayData}
            margin={{ top: 5, right: 20, left: 10, bottom: 20 }}
            barCategoryGap="20%"
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#27272a"
              horizontal={false}
            />
            <XAxis
              type="number"
              domain={[0, maxWeeks]}
              tick={{ fill: "#71717a", fontSize: 10 }}
              axisLine={{ stroke: "#3f3f46" }}
              tickLine={false}
              tickFormatter={(v) => `第${v}周`}
              label={{
                value: "（周）",
                position: "insideBottomRight",
                offset: -5,
                fill: "#52525b",
                fontSize: 10,
              }}
            />
            <YAxis
              type="category"
              dataKey="name"
              width={140}
              tick={{ fill: "#a1a1aa", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />

            {/* Invisible spacer bar */}
            <Bar dataKey="startDisplay" stackId="gantt" fill="transparent" isAnimationActive={false} />

            {/* Actual duration bar with per-row color */}
            <Bar dataKey="durationDisplay" stackId="gantt" name="认证周期" radius={[3, 3, 3, 3]} isAnimationActive={true}>
              {displayData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} fillOpacity={0.85} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="text-center text-[10px] text-zinc-600 mt-1">
        * 时间线为参考估算，实际周期因产品复杂度和机构工作量而异
      </p>
    </div>
  );
}

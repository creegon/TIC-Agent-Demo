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
import { type TimelineItem } from "@/lib/api";

interface Props {
  markets: string[];
  timelineData?: TimelineItem[] | null;
}

interface TooltipProps {
  active?: boolean;
  payload?: Array<{ payload: TimelineItem & { startDisplay: number; durationDisplay: number } }>;
}

function CustomTooltip({ active, payload }: TooltipProps) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div
      className="rounded-lg px-3 py-2 text-xs shadow-lg border"
      style={{
        backgroundColor: "#ffffff",
        borderColor: "#e5e5e5",
        color: "#0d0d0d",
        maxWidth: 240,
      }}
    >
      <p className="font-semibold text-zinc-800 mb-1">{d.name}</p>
      <p className="text-zinc-600">
        市场：<span className="font-medium text-zinc-800">{d.market}</span>
      </p>
      <p className="text-zinc-600">
        开始：第 <span className="font-medium text-zinc-800">{d.start}</span> 周
      </p>
      <p className="text-zinc-600">
        周期：<span className="font-medium" style={{ color: "#10a37f" }}>{d.duration} 周</span>
      </p>
      {d.source && (
        <p className="text-zinc-400 mt-1 text-[10px] border-t pt-1" style={{ borderColor: "#e5e5e5" }}>
          {d.source}
        </p>
      )}
    </div>
  );
}

function NoDataState() {
  return (
    <div
      className="flex flex-col items-center justify-center rounded-lg border py-10"
      style={{ backgroundColor: "#f7f7f8", borderColor: "#e5e5e5", minHeight: 200 }}
    >
      <p className="text-sm font-medium text-zinc-500 mb-1">时间线数据待补充</p>
      <p className="text-xs text-zinc-400 text-center max-w-xs">
        报告中未找到具体认证周期数字，无法生成时间线图。请参阅报告正文中各认证预估周期描述。
      </p>
    </div>
  );
}

export function TimelineChart({ markets, timelineData }: Props) {
  // Only show chart if timelineData is explicitly provided from backend
  // Do NOT use hardcoded fallback data
  const rawData = timelineData && timelineData.length > 0 ? timelineData : null;

  if (!rawData) {
    return (
      <div className="w-full">
        <NoDataState />
        <p className="text-center text-[10px] text-zinc-400 mt-2">
          * 认证周期需在报告中明确提及方可生成图表
        </p>
      </div>
    );
  }

  // For Gantt simulation: stacked bars with transparent spacer
  const data = rawData.map((d) => ({
    ...d,
    startDisplay: d.start,
    durationDisplay: d.duration,
  }));

  const totalCount = data.length;
  const displayData = data.slice(0, 16);
  const isTruncated = totalCount > 16;
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
              stroke="#e5e5e5"
              horizontal={false}
            />
            <XAxis
              type="number"
              domain={[0, maxWeeks]}
              tick={{ fill: "#9ca3af", fontSize: 10 }}
              axisLine={{ stroke: "#e5e5e5" }}
              tickLine={false}
              tickFormatter={(v) => `第${v}周`}
              label={{
                value: "（周）",
                position: "insideBottomRight",
                offset: -5,
                fill: "#d1d5db",
                fontSize: 10,
              }}
            />
            <YAxis
              type="category"
              dataKey="name"
              width={140}
              tick={{ fill: "#6e6e80", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(0,0,0,0.03)" }} />

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
      {isTruncated && (
        <p className="text-center text-[11px] text-amber-500 mt-2">
          仅展示前 16 项，共 {totalCount} 项
        </p>
      )}
      <p className="text-center text-[10px] text-zinc-400 mt-1">
        认证周期提取自报告原文，为一般参考值，实际周期受认证机构排期、样品准备等因素影响。悬停查看来源。
      </p>
    </div>
  );
}

"use client";

import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { calculateComplianceScores, type ComplianceScores } from "@/lib/chart-data";
import { type RadarScore } from "@/lib/api";

interface Props {
  reportText: string;
  radarData?: RadarScore[] | null;
}

interface TooltipProps {
  active?: boolean;
  payload?: Array<{ value: number; name: string }>;
  label?: string;
}

function CustomTooltip({ active, payload, label }: TooltipProps) {
  if (!active || !payload?.length) return null;
  return (
    <div
      className="rounded-lg px-3 py-2 text-xs shadow-lg border"
      style={{
        backgroundColor: "#ffffff",
        borderColor: "#e5e5e5",
        color: "#0d0d0d",
      }}
    >
      <p className="font-semibold text-zinc-800 mb-1">{label}</p>
      <p style={{ color: "#10a37f" }}>
        合规覆盖度：<span className="font-bold">{payload[0].value}</span> / 100
      </p>
    </div>
  );
}

function NoDataState() {
  return (
    <div
      className="flex flex-col items-center justify-center rounded-lg border py-10"
      style={{ backgroundColor: "#f7f7f8", borderColor: "#e5e5e5", minHeight: 200 }}
    >
      <p className="text-sm font-medium text-zinc-500 mb-1">数据不足</p>
      <p className="text-xs text-zinc-400 text-center max-w-xs">
        报告中未检测到足够的合规标准关键词，无法生成雷达图
      </p>
    </div>
  );
}

export function ComplianceRadar({ reportText, radarData }: Props) {
  // Use backend-extracted data if available, else fallback to frontend keyword matching
  const data = radarData && radarData.length > 0
    ? radarData
    : calculateComplianceScores(reportText);

  if (!data || data.length === 0) {
    return <NoDataState />;
  }

  // Collect reasons for the legend
  const reasonItems = data.filter((d) => d.reason);

  return (
    <div className="w-full">
      <div style={{ height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
            <PolarGrid stroke="#e5e5e5" strokeDasharray="3 3" />
            <PolarAngleAxis
              dataKey="subject"
              tick={{ fill: "#6e6e80", fontSize: 11 }}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 100]}
              tick={{ fill: "#9ca3af", fontSize: 10 }}
              tickCount={5}
              axisLine={false}
            />
            <Radar
              name="合规覆盖度"
              dataKey="score"
              stroke="#10a37f"
              fill="#10a37f"
              fillOpacity={0.15}
              strokeWidth={2}
              dot={{ fill: "#10a37f", r: 3 }}
            />
            <Tooltip content={<CustomTooltip />} />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Score reasons */}
      {reasonItems.length > 0 && (
        <div
          className="mt-3 rounded-lg p-3 border"
          style={{ backgroundColor: "#f7f7f8", borderColor: "#e5e5e5" }}
        >
          <p className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider mb-2">
            评分依据
          </p>
          <div className="grid grid-cols-1 gap-1">
            {data.map((d, i) => (
              <div key={i} className="flex items-center justify-between gap-3 text-[10px]">
                <span className="text-zinc-600">{d.subject}</span>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <span style={{ color: "#10a37f" }} className="font-medium">{d.score}</span>
                  {d.reason && <span className="text-zinc-400 text-right max-w-[200px]">{d.reason}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

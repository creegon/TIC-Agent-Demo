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
import { calculateComplianceScores } from "@/lib/chart-data";

interface Props {
  reportText: string;
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
        backgroundColor: "#18181b",
        borderColor: "#3f3f46",
        color: "#fff",
      }}
    >
      <p className="font-semibold text-zinc-100 mb-1">{label}</p>
      <p style={{ color: "#d4830a" }}>
        合规覆盖度：<span className="font-bold">{payload[0].value}</span> / 100
      </p>
    </div>
  );
}

export function ComplianceRadar({ reportText }: Props) {
  const data = calculateComplianceScores(reportText);

  return (
    <div className="w-full" style={{ height: 300 }}>
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
          <PolarGrid stroke="#3f3f46" strokeDasharray="3 3" />
          <PolarAngleAxis
            dataKey="subject"
            tick={{ fill: "#a1a1aa", fontSize: 11 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: "#71717a", fontSize: 10 }}
            tickCount={5}
            axisLine={false}
          />
          <Radar
            name="合规覆盖度"
            dataKey="score"
            stroke="#d4830a"
            fill="#d4830a"
            fillOpacity={0.25}
            strokeWidth={2}
            dot={{ fill: "#d4830a", r: 3 }}
          />
          <Tooltip content={<CustomTooltip />} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}

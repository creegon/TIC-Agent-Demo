"use client";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ComplianceRadar } from "./compliance-radar";
import { CostComparison } from "./cost-comparison";
import { TimelineChart } from "./timeline-chart";

interface Props {
  reportText: string;
  markets: string[];
}

export function ChartTabs({ reportText, markets }: Props) {
  return (
    <div
      className="mt-6 rounded-xl border overflow-hidden"
      style={{
        backgroundColor: "oklch(0.10 0 0)",
        borderColor: "oklch(0.18 0 0)",
      }}
    >
      {/* Section header */}
      <div
        className="px-5 py-3 border-b flex items-center gap-2"
        style={{ borderColor: "oklch(0.16 0 0)" }}
      >
        <span className="text-xs font-semibold text-zinc-300">📊 数据可视化</span>
        <span className="text-[10px] text-zinc-600 ml-1">
          基于报告内容自动生成
        </span>
      </div>

      <div className="px-5 py-4">
        <Tabs defaultValue="radar" className="w-full">
          <TabsList
            className="mb-5 h-7"
            style={{
              backgroundColor: "oklch(0.13 0 0)",
              border: "1px solid oklch(0.2 0 0)",
            }}
          >
            <TabsTrigger
              value="radar"
              className="text-[11px] h-5 px-3 data-[state=active]:text-zinc-100"
              style={{ color: "oklch(0.55 0 0)" }}
            >
              🕸 合规雷达
            </TabsTrigger>
            <TabsTrigger
              value="cost"
              className="text-[11px] h-5 px-3 data-[state=active]:text-zinc-100"
              style={{ color: "oklch(0.55 0 0)" }}
            >
              💰 成本对比
            </TabsTrigger>
            <TabsTrigger
              value="timeline"
              className="text-[11px] h-5 px-3 data-[state=active]:text-zinc-100"
              style={{ color: "oklch(0.55 0 0)" }}
            >
              📅 认证时间线
            </TabsTrigger>
          </TabsList>

          <TabsContent value="radar">
            <ComplianceRadar reportText={reportText} />
          </TabsContent>

          <TabsContent value="cost">
            <CostComparison markets={markets} />
          </TabsContent>

          <TabsContent value="timeline">
            <TimelineChart markets={markets} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

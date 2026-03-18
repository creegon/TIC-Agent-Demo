"use client";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ComplianceRadar } from "./compliance-radar";
import { CostComparison } from "./cost-comparison";
import { TimelineChart } from "./timeline-chart";
import { type ChartsData } from "@/lib/api";

interface Props {
  reportText: string;
  markets: string[];
  chartsData?: ChartsData | null;
}

export function ChartTabs({ reportText, markets, chartsData }: Props) {
  return (
    <div
      className="mt-2 rounded-xl border overflow-hidden"
      style={{
        backgroundColor: "#ffffff",
        borderColor: "#e5e5e5",
      }}
    >
      {/* Section header */}
      <div
        className="px-5 py-3 border-b flex items-center gap-2"
        style={{ borderColor: "#e5e5e5", backgroundColor: "#f7f7f8" }}
      >
        <span className="text-xs font-semibold text-zinc-700">📊 数据可视化</span>
        <span className="text-[10px] text-zinc-400 ml-1">
          {chartsData ? "数据来自报告内容提取" : "基于报告内容自动生成"}
        </span>
      </div>

      <div className="px-5 py-4">
        <Tabs defaultValue="radar" className="w-full">
          <TabsList
            className="mb-5 h-7"
            style={{
              backgroundColor: "#f7f7f8",
              border: "1px solid #e5e5e5",
            }}
          >
            <TabsTrigger
              value="radar"
              className="text-[11px] h-5 px-3 data-[state=active]:text-zinc-800"
              style={{ color: "#6e6e80" }}
            >
              📋 法规识别
            </TabsTrigger>
            <TabsTrigger
              value="cost"
              className="text-[11px] h-5 px-3 data-[state=active]:text-zinc-800"
              style={{ color: "#6e6e80" }}
            >
              💰 成本对比
            </TabsTrigger>
            <TabsTrigger
              value="timeline"
              className="text-[11px] h-5 px-3 data-[state=active]:text-zinc-800"
              style={{ color: "#6e6e80" }}
            >
              📅 认证时间线
            </TabsTrigger>
          </TabsList>

          <TabsContent value="radar">
            <ComplianceRadar
              reportText={reportText}
              radarData={chartsData?.radar ?? undefined}
            />
          </TabsContent>

          <TabsContent value="cost">
            <CostComparison
              markets={markets}
              costData={chartsData?.costs ?? undefined}
            />
          </TabsContent>

          <TabsContent value="timeline">
            <TimelineChart
              markets={markets}
              timelineData={chartsData?.timeline ?? undefined}
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

"use client";

/**
 * ComplianceRadar — Regulation identification summary
 *
 * Instead of a meaningless keyword-frequency radar chart, this component
 * displays a structured table of actually-identified regulations/standards
 * extracted from the report text. Each entry shows the standard number,
 * what it covers, and whether the report discussed it in detail.
 *
 * This gives TIC professionals verifiable, countable data points.
 */

import { type RadarScore } from "@/lib/api";

// ── Standard identification from report text ────────────────────────

interface IdentifiedStandard {
  id: string;          // e.g. "EN 62368-1"
  category: string;    // e.g. "电气安全"
  mentioned: boolean;  // found in report
  detailed: boolean;   // has table/section discussing it
}

// Known standard patterns and their categories
const STANDARD_PATTERNS: { pattern: RegExp; category: string; label: string }[] = [
  // Safety
  { pattern: /EN\s*(?:IEC\s*)?62368[^\s,)]*/, category: "电气安全", label: "音视频/ICT设备安全" },
  { pattern: /EN\s*(?:IEC\s*)?60950[^\s,)]*/, category: "电气安全", label: "IT设备安全（旧版）" },
  { pattern: /UL\s*62368[^\s,)]*/, category: "电气安全", label: "UL安全标准" },
  { pattern: /UL\s*60950[^\s,)]*/, category: "电气安全", label: "UL IT安全（旧版）" },
  { pattern: /IEC\s*62368[^\s,)]*/, category: "电气安全", label: "IEC安全标准" },
  { pattern: /EN\s*(?:IEC\s*)?61558[^\s,)]*/, category: "电气安全", label: "变压器安全" },
  { pattern: /GB\s*4943[^\s,)]*/, category: "电气安全", label: "中国IT设备安全" },
  { pattern: /ASTM\s*F963[^\s,)]*/, category: "电气安全", label: "美国玩具安全" },
  { pattern: /EN\s*71[^\s,)]*/, category: "电气安全", label: "欧盟玩具安全" },
  // EMC
  { pattern: /EN\s*55032[^\s,)]*/, category: "电磁兼容", label: "多媒体设备发射" },
  { pattern: /EN\s*55035[^\s,)]*/, category: "电磁兼容", label: "多媒体设备抗扰" },
  { pattern: /EN\s*(?:IEC\s*)?61000[^\s,)]*/, category: "电磁兼容", label: "EMC通用标准" },
  { pattern: /CISPR\s*\d+[^\s,)]*/, category: "电磁兼容", label: "CISPR标准" },
  { pattern: /47\s*CFR\s*Part\s*15[^\s,)]*/, category: "电磁兼容", label: "FCC Part 15" },
  { pattern: /FCC\s*Part\s*15[^\s,)]*/, category: "电磁兼容", label: "FCC Part 15" },
  { pattern: /GB\s*9254[^\s,)]*/, category: "电磁兼容", label: "中国EMC标准" },
  // Chemical/Environmental
  { pattern: /RoHS[^\s,)]*/, category: "化学环保", label: "有害物质限制" },
  { pattern: /REACH[^\s,)]*/, category: "化学环保", label: "化学品注册评估" },
  { pattern: /WEEE[^\s,)]*/, category: "化学环保", label: "电子废弃物回收" },
  { pattern: /ErP[^\s,)]*(?:\s*2019\/1782)?/, category: "化学环保", label: "能效/生态设计" },
  { pattern: /(?:Regulation\s*\(EU\)\s*)?2019\/1782/, category: "化学环保", label: "外部电源能效" },
  // Certification marks
  { pattern: /CE\s*(?:认证|标志|marking)/, category: "认证标志", label: "CE认证" },
  { pattern: /FCC\s*(?:认证|ID|certification)/, category: "认证标志", label: "FCC认证" },
  { pattern: /CCC\s*(?:认证|标志)/, category: "认证标志", label: "中国强制认证" },
  { pattern: /PSE\s*(?:认证|标志|mark)/, category: "认证标志", label: "日本电气安全" },
  { pattern: /CPSIA/, category: "认证标志", label: "美国消费品安全" },
  { pattern: /CPSC/, category: "认证标志", label: "美国消费品安全委员会" },
  // Radio
  { pattern: /RED\s*(?:Directive|指令)?/, category: "无线电", label: "无线电设备指令" },
  { pattern: /EN\s*300\s*\d+[^\s,)]*/, category: "无线电", label: "ETSI无线标准" },
  { pattern: /SRRC/, category: "无线电", label: "中国无线电型号核准" },
];

function extractStandards(reportText: string): IdentifiedStandard[] {
  if (!reportText || reportText.length < 100) return [];

  const found = new Map<string, IdentifiedStandard>();

  for (const { pattern, category, label } of STANDARD_PATTERNS) {
    const match = reportText.match(pattern);
    if (match) {
      const id = match[0].trim();
      // Check if already found (dedup by label to avoid "EN 62368" and "EN IEC 62368" duplicating)
      const key = label;
      if (!found.has(key)) {
        // Check if detailed: appears in a table row (| ... id ... |) or has a dedicated section
        const tablePattern = new RegExp(`\\|[^|]*${id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}[^|]*\\|`);
        const detailed = tablePattern.test(reportText);
        found.set(key, { id, category, mentioned: true, detailed });
      }
    }
  }

  return Array.from(found.values()).sort((a, b) => {
    // Sort by category then by id
    if (a.category !== b.category) return a.category.localeCompare(b.category);
    return a.id.localeCompare(b.id);
  });
}

// ── Category colors ────────────────────────────────────────

const CATEGORY_COLORS: Record<string, string> = {
  "电气安全": "#ef4444",
  "电磁兼容": "#3b82f6",
  "化学环保": "#22c55e",
  "认证标志": "#f59e0b",
  "无线电": "#8b5cf6",
};

// ── Component ──────────────────────────────────────────────

interface Props {
  reportText: string;
  radarData?: RadarScore[] | null;
}

function NoDataState() {
  return (
    <div
      className="flex flex-col items-center justify-center rounded-lg border py-10"
      style={{ backgroundColor: "#f7f7f8", borderColor: "#e5e5e5", minHeight: 200 }}
    >
      <p className="text-sm font-medium text-zinc-500 mb-1">数据不足</p>
      <p className="text-xs text-zinc-400 text-center max-w-xs">
        报告中未检测到标准号或法规引用
      </p>
    </div>
  );
}

export function ComplianceRadar({ reportText }: Props) {
  const standards = extractStandards(reportText);

  if (standards.length === 0) {
    return <NoDataState />;
  }

  // Group by category
  const grouped = new Map<string, IdentifiedStandard[]>();
  for (const s of standards) {
    const list = grouped.get(s.category) || [];
    list.push(s);
    grouped.set(s.category, list);
  }

  const totalDetailed = standards.filter(s => s.detailed).length;

  return (
    <div className="w-full">
      {/* Summary bar */}
      <div
        className="flex items-center gap-4 rounded-lg px-4 py-3 mb-4 border"
        style={{ backgroundColor: "#f7f7f8", borderColor: "#e5e5e5" }}
      >
        <div className="text-center">
          <p className="text-2xl font-bold text-zinc-800">{standards.length}</p>
          <p className="text-[10px] text-zinc-500">识别到的法规/标准</p>
        </div>
        <div className="w-px h-8 bg-zinc-200" />
        <div className="text-center">
          <p className="text-2xl font-bold" style={{ color: "#10a37f" }}>{totalDetailed}</p>
          <p className="text-[10px] text-zinc-500">在报告中详细讨论</p>
        </div>
        <div className="w-px h-8 bg-zinc-200" />
        <div className="text-center">
          <p className="text-2xl font-bold text-zinc-400">{standards.length - totalDetailed}</p>
          <p className="text-[10px] text-zinc-500">仅提及未展开</p>
        </div>
      </div>

      {/* Standards by category */}
      <div className="space-y-3">
        {Array.from(grouped.entries()).map(([category, items]) => (
          <div key={category}>
            <div className="flex items-center gap-2 mb-1.5">
              <div
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: CATEGORY_COLORS[category] || "#6e6e80" }}
              />
              <span className="text-xs font-semibold text-zinc-700">{category}</span>
              <span className="text-[10px] text-zinc-400">({items.length}项)</span>
            </div>
            <div className="ml-4 space-y-1">
              {items.map((item, i) => (
                <div
                  key={i}
                  className="flex items-center gap-2 text-xs rounded px-2 py-1"
                  style={{ backgroundColor: item.detailed ? "rgba(16,163,127,0.06)" : "transparent" }}
                >
                  <span className="text-[10px]">{item.detailed ? "📋" : "📎"}</span>
                  <code
                    className="font-mono text-[11px] px-1 py-0.5 rounded"
                    style={{ backgroundColor: "#f0f0f0", color: "#0d0d0d" }}
                  >
                    {item.id}
                  </code>
                  <span className="text-zinc-400">—</span>
                  <span className={item.detailed ? "text-zinc-700" : "text-zinc-400"}>
                    {item.detailed ? "报告中有详细分析" : "报告中提及"}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Disclaimer */}
      <p className="text-[10px] text-zinc-400 mt-4 text-center leading-relaxed border-t pt-3" style={{ borderColor: "#e5e5e5" }}>
        以上法规/标准通过正则匹配从报告文本中识别。"详细分析"指该标准出现在报告的表格中。此统计仅反映报告内容，不代表完整的适用法规清单。
      </p>
    </div>
  );
}

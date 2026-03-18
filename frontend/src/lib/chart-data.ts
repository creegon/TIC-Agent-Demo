// ─────────────────────────────────────────────────────────────
// chart-data.ts — Types and radar scoring logic for compliance charts
// NOTE: Cost and timeline data are NO LONGER hardcoded here.
//       They come from the backend extract_report_data() call via api.ts.
// ─────────────────────────────────────────────────────────────

export interface ComplianceScores {
  subject: string;
  score: number;
  fullMark: number;
  reason?: string;
}

// ─────────────────────────────────────────────────────────────
// Compliance Scores from report text (keyword matching)
// Used as a fallback / frontend calculation when backend returns no radar data.
// ─────────────────────────────────────────────────────────────

const DIMENSION_KEYWORDS: Record<string, string[]> = {
  电气安全: [
    "IEC 60950", "IEC 60065", "IEC 62368", "UL 60950", "UL 62368",
    "LVD", "电气安全", "electrical safety", "绝缘", "接地", "漏电",
    "过载保护", "EN 60950", "EN 62368", "BS EN", "安全标准",
  ],
  EMC: [
    "EMC", "电磁兼容", "FCC Part 15", "FCC Part 18", "CISPR",
    "EN 55032", "EN 55035", "EN 61000", "IEC 61000", "辐射发射",
    "传导发射", "电磁干扰", "抗扰度", "ESD", "浪涌",
  ],
  化学物质: [
    "RoHS", "REACH", "SVHC", "有害物质", "卤素", "铅", "汞", "镉",
    "六价铬", "多溴联苯", "PBB", "PBDE", "ErP", "化学品",
  ],
  标签要求: [
    "标签", "标识", "label", "marking", "CE标志", "FCC ID",
    "CCC标志", "PSE标志", "能效标识", "警告标语", "说明书", "包装标注",
  ],
  环保法规: [
    "WEEE", "能效", "Energy Star", "碳排放", "环保", "回收",
    "可持续", "绿色", "低功耗", "待机功耗", "环境保护",
  ],
  认证要求: [
    "CE认证", "FCC认证", "CCC认证", "PSE认证", "KC认证",
    "SRRC", "型式认证", "自我声明", "DoC", "合格声明",
    "认证机构", "测试报告", "技术文件",
  ],
};

const DIMENSION_REASONS: Record<string, string> = {
  电气安全: "根据报告中涉及的电气安全标准数量评估",
  EMC: "根据报告中电磁兼容相关法规覆盖度评估",
  化学物质: "根据报告中RoHS/REACH等化学品法规覆盖度评估",
  标签要求: "根据报告中标签标识要求完整度评估",
  环保法规: "根据报告中能效与环保法规覆盖度评估",
  认证要求: "根据报告中认证流程描述完整度评估",
};

/**
 * Calculate compliance scores from report text using keyword matching.
 * Returns 6 dimension scores (0–100) with reasons, or [] if no keywords found.
 */
export function calculateComplianceScores(reportText: string): ComplianceScores[] {
  if (!reportText || reportText.trim().length < 50) {
    return [];
  }

  const text = reportText.toLowerCase();
  let totalHits = 0;

  const results = Object.entries(DIMENSION_KEYWORDS).map(([subject, keywords]) => {
    let hits = 0;
    for (const kw of keywords) {
      if (text.includes(kw.toLowerCase())) {
        hits++;
      }
    }
    totalHits += hits;
    const raw = Math.min(hits / 8, 1);
    const score = Math.round(45 + raw * 50);
    return {
      subject,
      score,
      fullMark: 100,
      reason: DIMENSION_REASONS[subject],
    };
  });

  // Return empty array if no keywords found (insufficient data)
  if (totalHits === 0) return [];
  return results;
}

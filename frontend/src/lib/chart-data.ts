// ─────────────────────────────────────────────────────────────
// chart-data.ts — Data calculation logic for compliance charts
// ─────────────────────────────────────────────────────────────

export interface ComplianceScores {
  subject: string;
  score: number;
  fullMark: number;
}

export interface CertCostData {
  market: string;
  testingFee: number;
  certFee: number;
  annualFee: number;
}

export interface TimelineData {
  name: string;
  market: string;
  start: number;
  duration: number;
  color: string;
}

// ─────────────────────────────────────────────────────────────
// 1. Compliance Scores from report text
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
    "restricted substances",
  ],
  标签要求: [
    "标签", "标识", "label", "marking", "CE标志", "FCC ID",
    "CCC标志", "PSE标志", "能效标识", "警告标语", "说明书",
    "包装标注", "型号", "序列号",
  ],
  环保法规: [
    "WEEE", "能效", "ErP", "能源之星", "Energy Star", "碳排放",
    "环保", "回收", "可持续", "绿色", "低功耗", "待机功耗",
    "环境保护", "循环经济",
  ],
  认证要求: [
    "CE认证", "FCC认证", "CCC认证", "PSE认证", "KC认证",
    "SRRC", "型式认证", "自我声明", "DoC", "合格声明",
    "认证机构", "测试报告", "技术文件", "TCF",
  ],
};

/**
 * Calculate compliance scores from report text using keyword matching.
 * Returns 6 dimension scores (0–100).
 */
export function calculateComplianceScores(reportText: string): ComplianceScores[] {
  if (!reportText || reportText.trim().length < 50) {
    // Return default mid-range scores when no text
    return Object.keys(DIMENSION_KEYWORDS).map((subject) => ({
      subject,
      score: 60,
      fullMark: 100,
    }));
  }

  const text = reportText.toLowerCase();

  return Object.entries(DIMENSION_KEYWORDS).map(([subject, keywords]) => {
    let hits = 0;
    for (const kw of keywords) {
      if (text.includes(kw.toLowerCase())) {
        hits++;
      }
    }

    // Heuristic: more keyword hits → higher coverage score
    // Max hits cap at 8 for 100 score
    const raw = Math.min(hits / 8, 1);
    // Scale to 45–95 range (never 0, never 100 — realistic)
    const score = Math.round(45 + raw * 50);

    return { subject, score, fullMark: 100 };
  });
}

// ─────────────────────────────────────────────────────────────
// 2. Market Certification Costs
// Reference: knowledge_base.py cost estimates
// ─────────────────────────────────────────────────────────────

const COST_DATABASE: Record<string, { testingFee: number; certFee: number; annualFee: number }> = {
  欧盟: { testingFee: 8000, certFee: 5000, annualFee: 2000 },
  美国: { testingFee: 12000, certFee: 8000, annualFee: 3000 },
  中国: { testingFee: 15000, certFee: 10000, annualFee: 5000 },
  日本: { testingFee: 10000, certFee: 7000, annualFee: 2500 },
  韩国: { testingFee: 8000, certFee: 6000, annualFee: 2000 },
  英国: { testingFee: 7000, certFee: 4500, annualFee: 1800 },
  澳大利亚: { testingFee: 9000, certFee: 6000, annualFee: 2200 },
  巴西: { testingFee: 11000, certFee: 8000, annualFee: 3500 },
  印度: { testingFee: 7000, certFee: 5000, annualFee: 1500 },
  东南亚: { testingFee: 6000, certFee: 4000, annualFee: 1200 },
};

const DEFAULT_COST = { testingFee: 8000, certFee: 5000, annualFee: 2000 };

/**
 * Returns cost breakdown for each market (USD).
 */
export function getMarketCertCosts(markets: string[]): CertCostData[] {
  if (!markets || markets.length === 0) {
    return Object.entries(COST_DATABASE)
      .slice(0, 4)
      .map(([market, costs]) => ({ market, ...costs }));
  }

  return markets.map((market) => {
    // Try exact match first, then partial match
    const exactKey = Object.keys(COST_DATABASE).find((k) => k === market);
    const partialKey = Object.keys(COST_DATABASE).find(
      (k) => market.includes(k) || k.includes(market)
    );
    const costs = COST_DATABASE[exactKey ?? partialKey ?? ""] ?? DEFAULT_COST;
    return { market, ...costs };
  });
}

// ─────────────────────────────────────────────────────────────
// 3. Market Certification Timelines
// ─────────────────────────────────────────────────────────────

const MARKET_COLORS: Record<string, string> = {
  欧盟: "#1a3a5c",
  美国: "#d4830a",
  中国: "#e8a838",
  日本: "#2d6a9f",
  韩国: "#7c3aed",
  英国: "#059669",
  澳大利亚: "#dc2626",
  巴西: "#065f46",
  印度: "#b45309",
  东南亚: "#4338ca",
};

const DEFAULT_COLOR = "#52525b";

interface CertPhase {
  name: string;
  start: number;
  duration: number;
}

const TIMELINE_DATABASE: Record<string, CertPhase[]> = {
  欧盟: [
    { name: "CE — 准备技术文件", start: 0, duration: 4 },
    { name: "CE — EMC测试", start: 4, duration: 4 },
    { name: "CE — 安全测试", start: 4, duration: 6 },
    { name: "CE — 签发DoC", start: 10, duration: 2 },
  ],
  美国: [
    { name: "FCC — 预测试", start: 0, duration: 3 },
    { name: "FCC — 授权测试", start: 3, duration: 6 },
    { name: "FCC — 申请认证", start: 9, duration: 4 },
  ],
  中国: [
    { name: "CCC — 工厂检查", start: 0, duration: 4 },
    { name: "CCC — 型式试验", start: 4, duration: 8 },
    { name: "CCC — 证书审批", start: 12, duration: 4 },
  ],
  日本: [
    { name: "PSE — 测试申请", start: 0, duration: 2 },
    { name: "PSE — 型式试验", start: 2, duration: 8 },
    { name: "PSE — 认证发放", start: 10, duration: 3 },
  ],
  韩国: [
    { name: "KC — 测试", start: 0, duration: 6 },
    { name: "KC — 认证申请", start: 6, duration: 4 },
  ],
  英国: [
    { name: "UKCA — 文件准备", start: 0, duration: 3 },
    { name: "UKCA — 测试", start: 3, duration: 5 },
    { name: "UKCA — 声明签发", start: 8, duration: 2 },
  ],
};

const DEFAULT_TIMELINE: CertPhase[] = [
  { name: "测试准备", start: 0, duration: 4 },
  { name: "正式测试", start: 4, duration: 6 },
  { name: "认证申请", start: 10, duration: 4 },
];

/**
 * Returns timeline phases for each market.
 */
export function getMarketTimelines(markets: string[]): TimelineData[] {
  if (!markets || markets.length === 0) {
    return Object.entries(TIMELINE_DATABASE)
      .slice(0, 3)
      .flatMap(([market, phases]) =>
        phases.map((p) => ({
          name: `${market} — ${p.name}`,
          market,
          start: p.start,
          duration: p.duration,
          color: MARKET_COLORS[market] ?? DEFAULT_COLOR,
        }))
      );
  }

  return markets.flatMap((market) => {
    const exactKey = Object.keys(TIMELINE_DATABASE).find((k) => k === market);
    const partialKey = Object.keys(TIMELINE_DATABASE).find(
      (k) => market.includes(k) || k.includes(market)
    );
    const phases = TIMELINE_DATABASE[exactKey ?? partialKey ?? ""] ?? DEFAULT_TIMELINE;
    const color = MARKET_COLORS[exactKey ?? partialKey ?? market] ?? DEFAULT_COLOR;

    return phases.map((p) => ({
      name: p.name,
      market,
      start: p.start,
      duration: p.duration,
      color,
    }));
  });
}

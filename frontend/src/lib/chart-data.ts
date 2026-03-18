// ─────────────────────────────────────────────────────────────
// chart-data.ts — Type definitions for compliance chart data
//
// NOTE: All chart data now comes from the backend extract_report_data().
// The old keyword-count "scoring" logic has been REMOVED because it
// produced meaningless numbers that misled users.
//
// The ComplianceRadar component now does its own standard-identification
// directly from report text (extracting actual standard numbers like
// EN 62368-1, FCC Part 15, etc.) instead of counting keyword frequencies.
// ─────────────────────────────────────────────────────────────

export interface ComplianceScores {
  subject: string;
  score: number;
  fullMark: number;
  reason?: string;
  coverage?: string;
}

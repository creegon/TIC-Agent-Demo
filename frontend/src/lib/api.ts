// src/lib/api.ts — TIC Agent SSE API client (native fetch, no EventSource lib)

import { getSettings } from "@/lib/settings";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "";

function authHeaders(): Record<string, string> {
  const s = getSettings();
  const h: Record<string, string> = { "Content-Type": "application/json" };
  if (!s.useServerDefault) {
    if (s.googleAiKey) h["X-Google-AI-Key"] = s.googleAiKey;
    if (s.braveApiKey) h["X-Brave-API-Key"] = s.braveApiKey;
  }
  // useServerDefault → no key headers, backend uses its own keys
  return h;
}

// ─────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────

export interface AnalyzeRequest {
  product: string;
  markets: string[];
  extra_info?: string;
}

// Chart data types returned from backend extraction
export interface RadarScore {
  subject: string;
  score: number;
  fullMark: number;
  reason?: string;
  coverage?: string;  // ✅ / ⚠️ / ❌
}

export interface CostData {
  market: string;
  testingFee: number;
  certFee: number;
  annualFee: number;
  source?: string;  // source snippet from report text for tooltip
}

export interface TimelineItem {
  name: string;
  market: string;
  start: number;
  duration: number;
  color: string;
  source?: string;  // source annotation for tooltip
}

export interface ChartsData {
  radar: RadarScore[] | null;
  costs: CostData[] | null;
  timeline: TimelineItem[] | null;
}

export interface AnalyzeCallbacks {
  onStatus: (text: string) => void;
  onViz: (data: unknown) => void;
  onChunk: (text: string) => void;
  onDone: (fullReport: string, charts?: ChartsData) => void;
  onError: (msg: string) => void;
}

export interface FollowUpCallbacks {
  onChunk: (text: string) => void;
  onDone: () => void;
  onError: (msg: string) => void;
}

// ─────────────────────────────────────────────────────────────
// SSE stream reader helper
// ─────────────────────────────────────────────────────────────

async function consumeSSE(
  url: string,
  body: unknown,
  onEvent: (eventType: string, data: string) => void,
): Promise<void> {
  const response = await fetch(url, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  if (!response.body) {
    throw new Error("Response body is null");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  // Per SSE spec: event type and data accumulate until an empty line dispatches the event
  let currentEventType = "message";
  let dataLines: string[] = [];

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      // Flush any remaining buffered event on stream close
      if (dataLines.length > 0) {
        onEvent(currentEventType, dataLines.join("\n"));
      }
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (line.startsWith("event: ")) {
        // Set event type; stays valid until the event is dispatched (empty line)
        currentEventType = line.slice(7).trim();
      } else if (line.startsWith("data: ")) {
        // Accumulate data lines; multiple data: lines belong to the same event
        dataLines.push(line.slice(6));
      } else if (line === "" || line === "\r") {
        // Empty line = end of SSE event block; dispatch if we have data
        if (dataLines.length > 0) {
          onEvent(currentEventType, dataLines.join("\n"));
        }
        // Reset for next event
        currentEventType = "message";
        dataLines = [];
      }
      // Lines starting with ":" are SSE comments — ignore
      // All other lines are ignored per spec
    }
  }
}

// ─────────────────────────────────────────────────────────────
// analyzeProduct — POST /api/analyze
// ─────────────────────────────────────────────────────────────

export async function analyzeProduct(
  data: AnalyzeRequest,
  callbacks: AnalyzeCallbacks,
): Promise<void> {
  const { onStatus, onViz, onChunk, onDone, onError } = callbacks;

  try {
    await consumeSSE(
      `${API_BASE}/api/analyze`,
      {
        product: data.product,
        markets: data.markets,
        extra_info: data.extra_info ?? "",
      },
      (eventType, rawData) => {
        switch (eventType) {
          case "status":
            onStatus(rawData);
            break;

          case "viz": {
            try {
              const parsed = JSON.parse(rawData);
              onViz(parsed);
            } catch {
              // ignore malformed VIZ
            }
            break;
          }

          case "chunk":
            onChunk(rawData);
            break;

          case "done": {
            try {
              const parsed = JSON.parse(rawData) as { report: string; charts?: ChartsData };
              onDone(parsed.report, parsed.charts);
            } catch {
              onDone(rawData);
            }
            break;
          }

          case "error": {
            try {
              const parsed = JSON.parse(rawData) as { message: string };
              onError(parsed.message);
            } catch {
              onError(rawData);
            }
            break;
          }

          default:
            // unknown event — ignore
            break;
        }
      },
    );
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    onError(msg);
  }
}

// ─────────────────────────────────────────────────────────────
// exportPdf — POST /api/export-pdf
// ─────────────────────────────────────────────────────────────

export async function exportPdf(
  reportText: string,
  product: string,
  markets: string[],
): Promise<void> {
  const response = await fetch(`${API_BASE}/api/export-pdf`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ report_text: reportText, product, markets }),
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${product}_compliance_report.pdf`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// ─────────────────────────────────────────────────────────────
// fetchKnowledge — GET /api/knowledge
// ─────────────────────────────────────────────────────────────

export interface Regulation {
  standard_no: string;
  name: string;
  markets: string[];
  mandatory: boolean;
  description?: string;
  key_tests?: string[];
}

export interface KnowledgeResponse {
  regulations: Regulation[];
  category: string;
}

export async function fetchKnowledge(
  product: string,
  markets: string[],
): Promise<KnowledgeResponse> {
  const marketsParam = markets.join(",");
  const response = await fetch(
    `${API_BASE}/api/knowledge?product=${encodeURIComponent(product)}&markets=${encodeURIComponent(marketsParam)}`,
  );

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json() as Promise<KnowledgeResponse>;
}

// ─────────────────────────────────────────────────────────────
// followUp — POST /api/followup
// ─────────────────────────────────────────────────────────────

export async function followUp(
  messages: Array<{ role: string; content: string }>,
  question: string,
  callbacks: FollowUpCallbacks,
): Promise<void> {
  const { onChunk, onDone, onError } = callbacks;

  try {
    await consumeSSE(
      `${API_BASE}/api/followup`,
      { messages, question },
      (eventType, rawData) => {
        switch (eventType) {
          case "chunk":
            onChunk(rawData);
            break;
          case "done":
            onDone();
            break;
          case "error": {
            try {
              const parsed = JSON.parse(rawData) as { message: string };
              onError(parsed.message);
            } catch {
              onError(rawData);
            }
            break;
          }
          default:
            break;
        }
      },
    );
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    onError(msg);
  }
}

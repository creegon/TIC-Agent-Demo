// src/lib/api.ts — TIC Agent SSE API client (native fetch, no EventSource lib)

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

// ─────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────

export interface AnalyzeRequest {
  product: string;
  markets: string[];
  extra_info?: string;
}

export interface AnalyzeCallbacks {
  onStatus: (text: string) => void;
  onViz: (data: unknown) => void;
  onChunk: (text: string) => void;
  onDone: (fullReport: string) => void;
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
    headers: { "Content-Type": "application/json" },
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
  let currentEventType = "message";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (line.startsWith("event: ")) {
        currentEventType = line.slice(7).trim();
      } else if (line.startsWith("data: ")) {
        const data = line.slice(6);
        onEvent(currentEventType, data);
        // Reset event type after consuming (SSE spec: each data block can have its own event)
        currentEventType = "message";
      } else if (line === "") {
        // Empty line = end of SSE block; reset event type
        currentEventType = "message";
      }
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
              const parsed = JSON.parse(rawData) as { report: string };
              onDone(parsed.report);
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
    headers: { "Content-Type": "application/json" },
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

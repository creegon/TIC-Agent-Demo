const STORAGE_KEY = "tic-agent-settings";

export interface TicSettings {
  useServerDefault: boolean;
  googleAiKey: string;
  braveApiKey: string;
}

const DEFAULTS: TicSettings = {
  useServerDefault: true,
  googleAiKey: "",
  braveApiKey: "",
};

export function getSettings(): TicSettings {
  if (typeof window === "undefined") return DEFAULTS;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULTS;
    return { ...DEFAULTS, ...JSON.parse(raw) };
  } catch {
    return DEFAULTS;
  }
}

export function saveSettings(s: TicSettings): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
}

export function isReady(): boolean {
  const s = getSettings();
  return s.useServerDefault || (s.googleAiKey.length > 0 && s.braveApiKey.length > 0);
}

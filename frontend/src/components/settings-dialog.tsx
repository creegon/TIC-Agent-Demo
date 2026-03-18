"use client";

import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogClose,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getSettings, saveSettings, type TicSettings } from "@/lib/settings";

export function SettingsDialog() {
  const [open, setOpen] = useState(false);
  const [settings, setSettings] = useState<TicSettings>({
    useServerDefault: true,
    googleAiKey: "",
    braveApiKey: "",
  });

  useEffect(() => {
    setSettings(getSettings());
  }, [open]);

  const handleSave = () => {
    saveSettings(settings);
    setOpen(false);
  };

  const configured = (v: string) => v.length > 0;
  const useCustom = !settings.useServerDefault;

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-colors cursor-pointer"
        style={{
          color: "#6e6e80",
          border: "1px solid #e5e5e5",
        }}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLElement).style.backgroundColor = "#f7f7f8";
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLElement).style.backgroundColor = "transparent";
        }}
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
          <circle cx="12" cy="12" r="3" />
        </svg>
        Settings
      </DialogTrigger>
      <DialogContent
        style={{
          backgroundColor: "#ffffff",
          border: "1px solid #e5e5e5",
          borderRadius: "12px",
          maxWidth: "480px",
        }}
      >
        <DialogHeader>
          <DialogTitle style={{ color: "#0d0d0d", fontSize: "18px" }}>
            API Settings
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-5 mt-2">
          {/* Mode toggle */}
          <div
            className="flex items-center gap-3 p-3 rounded-lg cursor-pointer"
            style={{ backgroundColor: "#f7f7f8", border: "1px solid #e5e5e5" }}
            onClick={() =>
              setSettings((s) => ({ ...s, useServerDefault: !s.useServerDefault }))
            }
          >
            <div
              className="w-10 h-5 rounded-full relative transition-colors"
              style={{
                backgroundColor: settings.useServerDefault ? "#10a37f" : "#d1d5db",
              }}
            >
              <div
                className="absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all"
                style={{
                  left: settings.useServerDefault ? "22px" : "2px",
                }}
              />
            </div>
            <div>
              <p className="text-sm font-medium" style={{ color: "#0d0d0d" }}>
                使用服务器默认
              </p>
              <p className="text-xs" style={{ color: "#6e6e80" }}>
                无需配置，直接使用服务器提供的 AI 服务
              </p>
            </div>
          </div>

          {/* Custom key section — collapsed when using server default */}
          {useCustom && (
            <div className="space-y-4 pt-1">
              {/* Google AI Key */}
              <div>
                <div className="flex items-center gap-2 mb-1.5">
                  <label
                    className="text-sm font-medium"
                    style={{ color: "#0d0d0d" }}
                  >
                    Google AI API Key
                  </label>
                  <span className="text-xs">
                    {configured(settings.googleAiKey) ? "✅" : "⚠️"}
                  </span>
                </div>
                <p className="text-xs mb-2" style={{ color: "#6e6e80" }}>
                  用于 Gemini 模型调用。获取：
                  <a
                    href="https://aistudio.google.com/apikey"
                    target="_blank"
                    rel="noreferrer"
                    style={{ color: "#10a37f" }}
                  >
                    {" "}
                    aistudio.google.com/apikey
                  </a>
                </p>
                <Input
                  type="password"
                  placeholder="AIzaSy..."
                  value={settings.googleAiKey}
                  onChange={(e) =>
                    setSettings((s) => ({ ...s, googleAiKey: e.target.value }))
                  }
                  style={{
                    backgroundColor: "#ffffff",
                    border: "1px solid #e5e5e5",
                    color: "#0d0d0d",
                  }}
                />
              </div>

              {/* Brave API Key */}
              <div>
                <div className="flex items-center gap-2 mb-1.5">
                  <label
                    className="text-sm font-medium"
                    style={{ color: "#0d0d0d" }}
                  >
                    Brave Search API Key
                  </label>
                  <span className="text-xs">
                    {configured(settings.braveApiKey) ? "✅" : "⚠️"}
                  </span>
                </div>
                <p className="text-xs mb-2" style={{ color: "#6e6e80" }}>
                  用于法规搜索。获取：
                  <a
                    href="https://brave.com/search/api/"
                    target="_blank"
                    rel="noreferrer"
                    style={{ color: "#10a37f" }}
                  >
                    {" "}
                    brave.com/search/api
                  </a>
                </p>
                <Input
                  type="password"
                  placeholder="BSA..."
                  value={settings.braveApiKey}
                  onChange={(e) =>
                    setSettings((s) => ({ ...s, braveApiKey: e.target.value }))
                  }
                  style={{
                    backgroundColor: "#ffffff",
                    border: "1px solid #e5e5e5",
                    color: "#0d0d0d",
                  }}
                />
              </div>
            </div>
          )}
        </div>

        <div className="flex justify-end gap-2 mt-4">
          <DialogClose
            className="inline-flex items-center justify-center rounded-md text-sm font-medium h-9 px-4 py-2 cursor-pointer"
            style={{
              border: "1px solid #e5e5e5",
              color: "#6e6e80",
              backgroundColor: "#ffffff",
            }}
          >
            取消
          </DialogClose>
          <Button
            onClick={handleSave}
            style={{
              backgroundColor: "#10a37f",
              color: "#ffffff",
              border: "none",
            }}
          >
            保存
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

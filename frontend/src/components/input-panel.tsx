"use client";

import { useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { ExampleCards } from "@/components/example-cards";

const MARKETS = [
  { id: "EU", label: "🇪🇺 欧盟 (EU)" },
  { id: "US", label: "🇺🇸 美国 (US)" },
  { id: "CN", label: "🇨🇳 中国 (CN)" },
  { id: "JP", label: "🇯🇵 日本 (JP)" },
  { id: "KR", label: "🇰🇷 韩国 (KR)" },
  { id: "AU", label: "🇦🇺 澳大利亚 (AU)" },
];

interface InputPanelProps {
  onSubmit: (data: {
    product: string;
    markets: string[];
    extraInfo: string;
  }) => void;
  isLoading: boolean;
}

export function InputPanel({ onSubmit, isLoading }: InputPanelProps) {
  const [product, setProduct] = useState("");
  const [markets, setMarkets] = useState<string[]>(["EU", "US"]);
  const [extraInfo, setExtraInfo] = useState("");

  const toggleMarket = (id: string) => {
    setMarkets((prev) =>
      prev.includes(id) ? prev.filter((m) => m !== id) : [...prev, id]
    );
  };

  const handleExampleSelect = (p: string, m: string[]) => {
    setProduct(p);
    setMarkets(m);
  };

  const handleSubmit = () => {
    if (!product.trim() || markets.length === 0) return;
    onSubmit({ product: product.trim(), markets, extraInfo: extraInfo.trim() });
  };

  const canSubmit = product.trim().length > 0 && markets.length > 0 && !isLoading;

  return (
    <aside
      className="flex flex-col gap-5 p-5 border-r overflow-y-auto"
      style={{
        width: "380px",
        minWidth: "380px",
        borderColor: "oklch(0.18 0 0)",
        backgroundColor: "#0a0a0a",
      }}
    >
      {/* Product description */}
      <div className="flex flex-col gap-2">
        <label className="text-xs font-medium text-zinc-300">
          产品描述
          <span className="ml-1 text-red-500">*</span>
        </label>
        <Textarea
          value={product}
          onChange={(e) => setProduct(e.target.value)}
          placeholder="描述您的产品，例如：无线蓝牙耳机，支持主动降噪，续航24小时..."
          className="resize-none text-sm min-h-[100px] border"
          style={{
            backgroundColor: "oklch(0.11 0 0)",
            borderColor: "oklch(0.22 0 0)",
            color: "oklch(0.92 0 0)",
          }}
          disabled={isLoading}
        />
        <p className="text-xs" style={{ color: "oklch(0.5 0 0)" }}>
          越详细越准确，包括材质、功能、使用场景
        </p>
      </div>

      {/* Target markets */}
      <div className="flex flex-col gap-2.5">
        <label className="text-xs font-medium text-zinc-300">
          目标市场
          <span className="ml-1 text-red-500">*</span>
        </label>
        <div className="grid grid-cols-2 gap-2">
          {MARKETS.map((market) => (
            <div
              key={market.id}
              className="flex items-center gap-2 rounded-md px-3 py-2 cursor-pointer border transition-colors"
              style={{
                backgroundColor: markets.includes(market.id)
                  ? "rgba(212, 131, 10, 0.08)"
                  : "oklch(0.11 0 0)",
                borderColor: markets.includes(market.id)
                  ? "rgba(212, 131, 10, 0.4)"
                  : "oklch(0.2 0 0)",
              }}
              onClick={() => !isLoading && toggleMarket(market.id)}
            >
              <Checkbox
                id={`market-${market.id}`}
                checked={markets.includes(market.id)}
                onCheckedChange={() => !isLoading && toggleMarket(market.id)}
                className="w-3.5 h-3.5"
                style={
                  markets.includes(market.id)
                    ? { accentColor: "#d4830a" }
                    : {}
                }
              />
              <label
                htmlFor={`market-${market.id}`}
                className="text-xs cursor-pointer select-none"
                style={{
                  color: markets.includes(market.id)
                    ? "oklch(0.88 0 0)"
                    : "oklch(0.65 0 0)",
                }}
              >
                {market.label}
              </label>
            </div>
          ))}
        </div>
        {markets.length === 0 && (
          <p className="text-xs text-red-500">请至少选择一个目标市场</p>
        )}
      </div>

      {/* Extra info */}
      <div className="flex flex-col gap-2">
        <label className="text-xs font-medium text-zinc-300">
          补充信息
          <span className="ml-1.5 text-xs font-normal" style={{ color: "oklch(0.5 0 0)" }}>
            （可选）
          </span>
        </label>
        <Textarea
          value={extraInfo}
          onChange={(e) => setExtraInfo(e.target.value)}
          placeholder="已有认证、特殊材料、目标用户群等..."
          className="resize-none text-sm min-h-[72px] border"
          style={{
            backgroundColor: "oklch(0.11 0 0)",
            borderColor: "oklch(0.22 0 0)",
            color: "oklch(0.92 0 0)",
          }}
          disabled={isLoading}
        />
      </div>

      {/* Submit button */}
      <button
        onClick={handleSubmit}
        disabled={!canSubmit}
        className="w-full py-2.5 rounded-md text-sm font-semibold transition-all"
        style={{
          backgroundColor: canSubmit ? "#d4830a" : "oklch(0.18 0 0)",
          color: canSubmit ? "#0a0a0a" : "oklch(0.45 0 0)",
          cursor: canSubmit ? "pointer" : "not-allowed",
        }}
        onMouseEnter={(e) => {
          if (canSubmit) {
            (e.currentTarget as HTMLElement).style.backgroundColor = "#bf7509";
          }
        }}
        onMouseLeave={(e) => {
          if (canSubmit) {
            (e.currentTarget as HTMLElement).style.backgroundColor = "#d4830a";
          }
        }}
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
            检查中...
          </span>
        ) : (
          "生成合规报告 →"
        )}
      </button>

      {/* Example cards */}
      <div
        className="border-t pt-4"
        style={{ borderColor: "oklch(0.16 0 0)" }}
      >
        <ExampleCards onSelect={handleExampleSelect} />
      </div>
    </aside>
  );
}

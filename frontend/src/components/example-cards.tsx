"use client";

const EXAMPLES = [
  {
    product: "蓝牙耳机",
    markets: ["EU", "US", "CN"],
    description: "无线音频设备",
    icon: "🎧",
  },
  {
    product: "儿童积木玩具",
    markets: ["EU", "US"],
    description: "3岁以上儿童玩具",
    icon: "🧩",
  },
  {
    product: "锂电池充电宝",
    markets: ["EU", "US", "CN", "JP"],
    description: "20000mAh移动电源",
    icon: "🔋",
  },
  {
    product: "不锈钢餐具",
    markets: ["EU", "CN"],
    description: "304不锈钢刀叉套装",
    icon: "🍴",
  },
];

interface ExampleCardsProps {
  onSelect: (product: string, markets: string[]) => void;
}

export function ExampleCards({ onSelect }: ExampleCardsProps) {
  return (
    <div className="mt-4">
      <p className="text-xs mb-2.5 font-medium" style={{ color: "oklch(0.55 0 0)" }}>
        快速示例
      </p>
      <div className="grid grid-cols-2 gap-2">
        {EXAMPLES.map((ex) => (
          <button
            key={ex.product}
            onClick={() => onSelect(ex.product, ex.markets)}
            className="text-left rounded-lg p-3 border transition-colors group"
            style={{
              backgroundColor: "oklch(0.13 0 0)",
              borderColor: "oklch(0.2 0 0)",
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.backgroundColor = "oklch(0.16 0 0)";
              (e.currentTarget as HTMLElement).style.borderColor = "oklch(0.26 0 0)";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.backgroundColor = "oklch(0.13 0 0)";
              (e.currentTarget as HTMLElement).style.borderColor = "oklch(0.2 0 0)";
            }}
          >
            <div className="flex items-center gap-1.5 mb-1">
              <span className="text-base leading-none">{ex.icon}</span>
              <span className="text-xs font-medium text-zinc-200 truncate">{ex.product}</span>
            </div>
            <p className="text-xs truncate mb-1.5" style={{ color: "oklch(0.55 0 0)" }}>
              {ex.description}
            </p>
            <div className="flex flex-wrap gap-1">
              {ex.markets.map((m) => (
                <span
                  key={m}
                  className="text-[10px] px-1.5 py-0.5 rounded font-medium"
                  style={{
                    backgroundColor: "oklch(0.18 0 0)",
                    color: "oklch(0.65 0 0)",
                  }}
                >
                  {m}
                </span>
              ))}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

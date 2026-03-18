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
      <p className="text-xs mb-2.5 font-medium" style={{ color: "#6e6e80" }}>
        快速示例
      </p>
      <div className="grid grid-cols-2 gap-2">
        {EXAMPLES.map((ex) => (
          <button
            key={ex.product}
            onClick={() => onSelect(ex.product, ex.markets)}
            className="text-left rounded-lg p-3 border transition-colors group"
            style={{
              backgroundColor: "#ffffff",
              borderColor: "#e5e5e5",
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.backgroundColor = "#ececf1";
              (e.currentTarget as HTMLElement).style.borderColor = "#d1d5db";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.backgroundColor = "#ffffff";
              (e.currentTarget as HTMLElement).style.borderColor = "#e5e5e5";
            }}
          >
            <div className="flex items-center gap-1.5 mb-1">
              <span className="text-base leading-none">{ex.icon}</span>
              <span className="text-xs font-medium text-zinc-700 truncate">{ex.product}</span>
            </div>
            <p className="text-xs truncate mb-1.5" style={{ color: "#6e6e80" }}>
              {ex.description}
            </p>
            <div className="flex flex-wrap gap-1">
              {ex.markets.map((m) => (
                <span
                  key={m}
                  className="text-[10px] px-1.5 py-0.5 rounded font-medium"
                  style={{
                    backgroundColor: "#f7f7f8",
                    color: "#6e6e80",
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

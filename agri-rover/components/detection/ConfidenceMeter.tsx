"use client";

interface ConfidenceMeterProps {
  confidence: number; // 0-1
}

export default function ConfidenceMeter({ confidence }: ConfidenceMeterProps) {
  const pct = Math.round(confidence * 100);
  const size = 160;
  const strokeW = 14;
  const r = (size - strokeW) / 2;
  const circ = Math.PI * r; // half circle
  const dash = (pct / 100) * circ;

  const getColor = (p: number) => {
    if (p >= 90) return "#22C55E";
    if (p >= 70) return "#FBBF24";
    return "#EF4444";
  };

  const color = getColor(pct);

  const label = pct >= 90 ? "Very High" : pct >= 70 ? "High" : pct >= 50 ? "Moderate" : "Low";

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size / 2 + strokeW / 2 }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="overflow-visible">
          {/* Background arc */}
          <path
            d={`M ${strokeW / 2} ${size / 2} A ${r} ${r} 0 0 1 ${size - strokeW / 2} ${size / 2}`}
            fill="none"
            stroke="#E5E7EB"
            strokeWidth={strokeW}
            strokeLinecap="round"
          />
          {/* Foreground arc */}
          <path
            d={`M ${strokeW / 2} ${size / 2} A ${r} ${r} 0 0 1 ${size - strokeW / 2} ${size / 2}`}
            fill="none"
            stroke={color}
            strokeWidth={strokeW}
            strokeLinecap="round"
            strokeDasharray={`${dash} ${circ}`}
            style={{
              filter: `drop-shadow(0 0 6px ${color}80)`,
              transition: "stroke-dasharray 1.2s ease-out",
            }}
          />
          {/* Center text */}
          <text x={size / 2} y={size / 2 - 4} textAnchor="middle" fontSize="30" fontWeight="800" fill={color} fontFamily="Plus Jakarta Sans, sans-serif">
            {pct}%
          </text>
          <text x={size / 2} y={size / 2 + 18} textAnchor="middle" fontSize="12" fontWeight="600" fill="#6B7280" fontFamily="Plus Jakarta Sans, sans-serif">
            {label} Confidence
          </text>
        </svg>
      </div>

      {/* Legend */}
      <div className="flex gap-4 mt-2">
        {[
          { label: "Very High", range: "90-100%", color: "#22C55E" },
          { label: "High", range: "70-89%", color: "#FBBF24" },
          { label: "Low", range: "<70%", color: "#EF4444" },
        ].map((item) => (
          <div key={item.label} className="flex items-center gap-1">
            <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
            <span className="text-[11px] text-gray-500">{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

"use client";

import { farmHealthSummary } from "@/lib/mock-data";
import { Leaf, AlertTriangle, XCircle, TrendingUp } from "lucide-react";

interface RingProps {
  pct: number;
  color: string;
  size?: number;
}

function RingChart({ pct, color, size = 80 }: RingProps) {
  const strokeWidth = 9;
  const r = (size - strokeWidth * 2) / 2;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;
  const cx = size / 2;
  const cy = size / 2;

  return (
    <svg width={size} height={size} style={{ display: "block" }}>
      {/* Background track */}
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="#E5E7EB" strokeWidth={strokeWidth} />
      {/* Progress arc — start from top (rotate -90deg around center) */}
      <circle
        cx={cx}
        cy={cy}
        r={r}
        fill="none"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeDasharray={`${dash} ${circ}`}
        strokeLinecap="round"
        transform={`rotate(-90 ${cx} ${cy})`}
        className="transition-all duration-1000 ease-out"
      />
      {/* Centered label — no rotation needed */}
      <text
        x={cx}
        y={cy}
        textAnchor="middle"
        dominantBaseline="central"
        fontSize={size < 80 ? 12 : 15}
        fontWeight="700"
        fill={color}
        fontFamily="Plus Jakarta Sans, system-ui, sans-serif"
      >
        {pct}%
      </text>
    </svg>
  );
}

const cards = [
  {
    label: "Healthy Plants",
    key: "healthy_pct" as const,
    count_key: "healthy" as const,
    color: "#22C55E",
    bg: "from-green-50 to-emerald-50",
    border: "border-green-200",
    icon: Leaf,
    iconBg: "bg-green-100",
    iconColor: "text-green-600",
    description: "No symptoms detected",
  },
  {
    label: "Need Attention",
    key: "attention_pct" as const,
    count_key: "attention" as const,
    color: "#FBBF24",
    bg: "from-yellow-50 to-amber-50",
    border: "border-yellow-200",
    icon: AlertTriangle,
    iconBg: "bg-yellow-100",
    iconColor: "text-yellow-600",
    description: "Early symptoms visible",
  },
  {
    label: "Diseased Plants",
    key: "diseased_pct" as const,
    count_key: "diseased" as const,
    color: "#EF4444",
    bg: "from-red-50 to-rose-50",
    border: "border-red-200",
    icon: XCircle,
    iconBg: "bg-red-100",
    iconColor: "text-red-600",
    description: "Urgent action needed",
  },
];

export default function HealthSummaryCards() {
  const summary = farmHealthSummary;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 animate-fade-in-up">
      {cards.map(({ label, key, count_key, color, bg, border, icon: Icon, iconBg, iconColor, description }) => (
        <div
          key={key}
          className={`card bg-gradient-to-br ${bg} border ${border} p-5 flex items-center gap-4 group hover:scale-[1.02] transition-transform duration-200`}
        >
          <div className="flex-shrink-0">
            <RingChart pct={summary[key]} color={color} size={80} />
          </div>
          <div className="flex-1 min-w-0">
            <div className={`inline-flex items-center gap-1.5 p-1.5 rounded-lg ${iconBg} mb-2`}>
              <Icon className={`w-4 h-4 ${iconColor}`} />
              <span className={`text-xs font-semibold ${iconColor}`}>{summary[key]}%</span>
            </div>
            <p className="text-2xl font-bold text-agri-text count-up">{summary[count_key]}</p>
            <p className="text-sm font-semibold text-agri-text">{label}</p>
            <p className="text-xs text-gray-500 mt-0.5">{description}</p>
          </div>
        </div>
      ))}

      {/* Total summary bar */}
      <div className="sm:col-span-3 card p-4 flex items-center gap-4">
        <TrendingUp className="w-5 h-5 text-leaf flex-shrink-0" />
        <div className="flex-1">
          <div className="flex gap-1 h-4 rounded-full overflow-hidden">
            <div
              className="bg-primary transition-all duration-700"
              style={{ width: `${summary.healthy_pct}%` }}
            />
            <div
              className="bg-warning transition-all duration-700"
              style={{ width: `${summary.attention_pct}%` }}
            />
            <div
              className="bg-danger transition-all duration-700"
              style={{ width: `${summary.diseased_pct}%` }}
            />
          </div>
        </div>
        <div className="flex items-center gap-3 text-xs text-gray-500 flex-shrink-0">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-primary inline-block" /> Healthy</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-warning inline-block" /> Attention</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-danger inline-block" /> Diseased</span>
          <span className="font-medium">{summary.total_cells} cells</span>
        </div>
      </div>
    </div>
  );
}

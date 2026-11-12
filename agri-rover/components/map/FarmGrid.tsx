"use client";

import { useRef, useState } from "react";
import { farmGrid } from "@/lib/mock-data";
import { DISEASE_DISPLAY_NAMES } from "@/lib/disease-info";

interface CellProps {
  row: number;
  col: number;
  status: string;
  diseaseClass: string;
  severity: string;
  section: string;
  lastChecked: string;
  detectionId?: string;
  onSelect: (info: CellInfo) => void;
}

interface CellInfo {
  row: number;
  col: number;
  section: string;
  status: string;
  diseaseClass: string;
  severity: string;
  lastChecked: string;
}

const STATUS_COLORS = {
  healthy: { fill: "#22C55E", shadow: "rgba(34,197,94,0.35)", ring: "#16A34A" },
  attention: { fill: "#FBBF24", shadow: "rgba(251,191,36,0.35)", ring: "#D97706" },
  diseased: { fill: "#EF4444", shadow: "rgba(239,68,68,0.35)", ring: "#B91C1C" },
};

const SEVERITY_LABELS: Record<string, string> = {
  healthy: "Healthy",
  early: "Early Stage",
  moderate: "Moderate",
  severe: "Severe",
};

function HexCell({ row, col, status, diseaseClass, severity, section, lastChecked, onSelect }: CellProps) {
  const [hovered, setHovered] = useState(false);
  const colors = STATUS_COLORS[status as keyof typeof STATUS_COLORS] ?? STATUS_COLORS.healthy;
  const isDiseased = status !== "healthy";

  return (
    <g
      onClick={() => onSelect({ row, col, section, status, diseaseClass, severity, lastChecked })}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className="cursor-pointer"
      style={{ filter: hovered ? `drop-shadow(0 0 8px ${colors.shadow})` : undefined }}
    >
      <polygon
        points="50,5 95,27.5 95,72.5 50,95 5,72.5 5,27.5"
        fill={colors.fill}
        stroke={hovered ? colors.ring : "white"}
        strokeWidth={hovered ? 3 : 2}
        opacity={hovered ? 1 : 0.88}
        style={{
          transition: "all 0.2s ease",
          transform: hovered ? "scale(1.06)" : "scale(1)",
          transformOrigin: "50px 50px",
        }}
      />

      {/* Pulse ring for diseased cells */}
      {isDiseased && (
        <polygon
          points="50,2 98,26 98,74 50,98 2,74 2,26"
          fill="none"
          stroke={colors.ring}
          strokeWidth={1.5}
          opacity={0.4}
          className="animate-pulse-slow"
        />
      )}

      {/* Row·Section label */}
      <text x="50" y="44" textAnchor="middle" fill="white" fontSize="11" fontWeight="700" fontFamily="Plus Jakarta Sans, sans-serif">
        R{row}{section}
      </text>

      {/* Status emoji */}
      <text x="50" y="66" textAnchor="middle" fontSize="16">
        {status === "healthy" ? "🌿" : status === "attention" ? "⚠️" : "🔴"}
      </text>
    </g>
  );
}

interface InfoDrawerProps {
  cell: CellInfo | null;
  onClose: () => void;
}

function InfoDrawer({ cell, onClose }: InfoDrawerProps) {
  if (!cell) return null;
  const colors = STATUS_COLORS[cell.status as keyof typeof STATUS_COLORS] ?? STATUS_COLORS.healthy;

  return (
    <div className="absolute right-0 top-0 bottom-0 w-72 bg-white border-l border-green-100 shadow-card-hover rounded-r-2xl p-5 animate-slide-in-right z-10">
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-xs text-gray-400 font-semibold uppercase tracking-wider">Cell Details</p>
          <h4 className="text-lg font-bold text-agri-text mt-0.5">
            Row {cell.row}, Section {cell.section}
          </h4>
        </div>
        <button onClick={onClose} className="w-7 h-7 rounded-lg bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-500 text-sm transition-colors">
          ✕
        </button>
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between p-3 rounded-xl" style={{ backgroundColor: colors.shadow.replace("0.35", "0.1") }}>
          <span className="text-sm font-medium text-gray-600">Status</span>
          <span className="text-sm font-bold capitalize" style={{ color: colors.fill }}>
            {cell.status}
          </span>
        </div>

        <div className="p-3 bg-gray-50 rounded-xl">
          <p className="text-xs text-gray-500 mb-1">Disease</p>
          <p className="text-sm font-semibold text-agri-text">
            {DISEASE_DISPLAY_NAMES[cell.diseaseClass as keyof typeof DISEASE_DISPLAY_NAMES]}
          </p>
        </div>

        <div className="p-3 bg-gray-50 rounded-xl">
          <p className="text-xs text-gray-500 mb-1">Severity</p>
          <p className="text-sm font-semibold text-agri-text">{SEVERITY_LABELS[cell.severity]}</p>
        </div>

        <div className="p-3 bg-gray-50 rounded-xl">
          <p className="text-xs text-gray-500 mb-1">Last Checked</p>
          <p className="text-sm font-semibold text-agri-text">
            {new Date(cell.lastChecked).toLocaleString("en-IN")}
          </p>
        </div>
      </div>
    </div>
  );
}

export default function FarmGrid() {
  const [selectedCell, setSelectedCell] = useState<CellInfo | null>(null);

  const ROWS = 5;
  const COLS = 4;
  const HEX_W = 100;
  const HEX_H = 90;
  const GAP_X = 8;
  const GAP_Y = 8;

  const svgW = COLS * (HEX_W + GAP_X) + HEX_W / 2;
  const svgH = ROWS * (HEX_H * 0.75 + GAP_Y) + HEX_H * 0.25;

  const getCellPos = (row: number, col: number) => {
    const r = row - 1;
    const c = col - 1;
    const x = c * (HEX_W + GAP_X) + (r % 2 === 0 ? 0 : HEX_W / 2 + GAP_X / 2);
    const y = r * (HEX_H * 0.75 + GAP_Y);
    return { x, y };
  };

  return (
    <div className="card p-5 animate-fade-in-up">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-agri-text">Pandal Farm Map</h3>
          <p className="text-xs text-gray-400">5 rows × 4 sections — click a cell for details</p>
        </div>
        <div className="flex items-center gap-3">
          {[
            { color: "#22C55E", label: "Healthy" },
            { color: "#FBBF24", label: "Attention" },
            { color: "#EF4444", label: "Diseased" },
          ].map(({ color, label }) => (
            <div key={label} className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
              <span className="text-xs text-gray-500">{label}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="relative">
        <div className="overflow-auto">
          <svg
            width={svgW}
            height={svgH}
            viewBox={`0 0 ${svgW} ${svgH}`}
            className="mx-auto"
            style={{ maxWidth: "100%" }}
          >
            {farmGrid.map((cell) => {
              const { x, y } = getCellPos(cell.row, cell.col);
              return (
                <g key={`${cell.row}-${cell.col}`} transform={`translate(${x}, ${y})`}>
                  <HexCell
                    row={cell.row}
                    col={cell.col}
                    status={cell.status}
                    diseaseClass={cell.disease_class}
                    severity={cell.severity}
                    section={cell.section}
                    lastChecked={cell.last_checked}
                    detectionId={cell.detection_id}
                    onSelect={setSelectedCell}
                  />
                </g>
              );
            })}
          </svg>
        </div>

        {selectedCell && (
          <InfoDrawer cell={selectedCell} onClose={() => setSelectedCell(null)} />
        )}
      </div>
    </div>
  );
}

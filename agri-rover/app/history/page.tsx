"use client";

import { historicalDetections, trendData, diseaseDistribution } from "@/lib/mock-data";
import { DISEASE_DISPLAY_NAMES, SEVERITY_CONFIG } from "@/lib/disease-info";
import { formatTimestamp } from "@/lib/utils";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar,
} from "recharts";
import { Clock, MapPin, Activity } from "lucide-react";

export default function HistoryPage() {
  return (
    <div className="space-y-6">
      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Area chart – trend */}
        <div className="lg:col-span-2 card p-5">
          <h3 className="text-base font-semibold text-agri-text mb-4">📈 Disease Trend (14 Days)</h3>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={trendData} margin={{ top: 4, right: 12, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="gHealthy" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22C55E" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#22C55E" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gAttention" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#FBBF24" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#FBBF24" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gDiseased" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#EF4444" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#9CA3AF" }} />
              <YAxis tick={{ fontSize: 11, fill: "#9CA3AF" }} />
              <Tooltip
                contentStyle={{ borderRadius: 12, border: "1px solid #E5E7EB", fontSize: 12 }}
              />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Area type="monotone" dataKey="healthy" name="Healthy" stroke="#22C55E" strokeWidth={2} fill="url(#gHealthy)" />
              <Area type="monotone" dataKey="attention" name="Attention" stroke="#FBBF24" strokeWidth={2} fill="url(#gAttention)" />
              <Area type="monotone" dataKey="diseased" name="Diseased" stroke="#EF4444" strokeWidth={2} fill="url(#gDiseased)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Pie chart – disease distribution */}
        <div className="card p-5">
          <h3 className="text-base font-semibold text-agri-text mb-4">🥧 Disease Distribution</h3>
          <ResponsiveContainer width="100%" height={160}>
            <PieChart>
              <Pie
                data={diseaseDistribution}
                cx="50%"
                cy="50%"
                innerRadius={45}
                outerRadius={75}
                paddingAngle={3}
                dataKey="value"
              >
                {diseaseDistribution.map((entry, index) => (
                  <Cell key={index} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ borderRadius: 12, fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-1.5 mt-2">
            {diseaseDistribution.map((d) => (
              <div key={d.name} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: d.color }} />
                  <span className="text-gray-600">{d.name}</span>
                </div>
                <span className="font-semibold text-agri-text">{d.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Section comparison bar chart */}
      <div className="card p-5">
        <h3 className="text-base font-semibold text-agri-text mb-4">📊 Detections by Section</h3>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart
            data={[
              { section: "Section A", detections: 2, diseased: 1 },
              { section: "Section B", detections: 3, diseased: 2 },
              { section: "Section C", detections: 2, diseased: 1 },
              { section: "Section D", detections: 3, diseased: 1 },
            ]}
            margin={{ top: 0, right: 12, left: -20, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
            <XAxis dataKey="section" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip contentStyle={{ borderRadius: 12, fontSize: 12 }} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Bar dataKey="detections" name="Total Scans" fill="#22C55E" radius={[4, 4, 0, 0]} />
            <Bar dataKey="diseased" name="Disease Found" fill="#EF4444" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Detection timeline */}
      <div className="card p-5">
        <h3 className="text-base font-semibold text-agri-text mb-4">📅 Detection Timeline</h3>
        <div className="space-y-3">
          {historicalDetections.map((det) => {
            const dr = det.detection_result;
            const sev = SEVERITY_CONFIG[dr.severity_class];
            const displayName = DISEASE_DISPLAY_NAMES[dr.disease_class];

            return (
              <div
                key={det.id}
                className="flex items-center gap-4 p-4 rounded-xl hover:bg-green-50 border border-green-100/50 transition-colors group"
              >
                {/* Color dot */}
                <div
                  className="w-3 h-3 rounded-full flex-shrink-0"
                  style={{ backgroundColor: sev.color }}
                />

                {/* Disease name */}
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-agri-text text-sm truncate">{displayName}</p>
                  <div className="flex items-center gap-3 mt-0.5">
                    <span className="flex items-center gap-1 text-xs text-gray-400">
                      <MapPin className="w-3 h-3" />
                      R{det.rover_location.row}–{det.rover_location.section}
                    </span>
                    <span className="flex items-center gap-1 text-xs text-gray-400">
                      <Activity className="w-3 h-3" />
                      {Math.round(dr.confidence * 100)}% confidence
                    </span>
                  </div>
                </div>

                {/* Affected */}
                <div className="text-right hidden sm:block">
                  <p className="text-sm font-bold" style={{ color: sev.color }}>
                    {dr.affected_area_percentage}%
                  </p>
                  <p className="text-[11px] text-gray-400">affected</p>
                </div>

                {/* Severity badge */}
                <span
                  className="px-2.5 py-1 rounded-full text-[11px] font-bold flex-shrink-0 border"
                  style={{ color: sev.color, backgroundColor: sev.bg, borderColor: sev.color + "40" }}
                >
                  {sev.label}
                </span>

                {/* Time */}
                <div className="text-right hidden md:block flex-shrink-0">
                  <p className="text-xs text-gray-400 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {formatTimestamp(det.timestamp)}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

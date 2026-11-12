"use client";

import { historicalDetections } from "@/lib/mock-data";
import { DISEASE_DISPLAY_NAMES } from "@/lib/disease-info";
import { Activity, AlertOctagon, Bug } from "lucide-react";

export default function QuickStatsBar() {
  const dets = historicalDetections;
  const diseased = dets.filter((d) => d.detection_result.severity_class === "severe").length;
  const avgConfidence = Math.round(
    (dets.reduce((sum, d) => sum + d.detection_result.confidence, 0) / dets.length) * 100
  );
  const mostCommon = Object.entries(
    dets.reduce((acc: Record<string, number>, d) => {
      const dc = d.detection_result.disease_class;
      if (dc !== "healthy") acc[dc] = (acc[dc] || 0) + 1;
      return acc;
    }, {})
  ).sort((a, b) => b[1] - a[1])[0];

  return (
    <div className="grid grid-cols-3 gap-4 animate-fade-in-up">
      {/* Severe Cases */}
      <div className="card p-4 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-red-100 flex items-center justify-center flex-shrink-0">
          <AlertOctagon className="w-5 h-5 text-red-500" />
        </div>
        <div>
          <p className="text-2xl font-bold text-agri-text">{diseased}</p>
          <p className="text-xs text-gray-500">Severe Cases</p>
        </div>
      </div>

      {/* Avg Confidence */}
      <div className="card p-4 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
          <Activity className="w-5 h-5 text-primary" />
        </div>
        <div>
          <p className="text-2xl font-bold text-agri-text">{avgConfidence}%</p>
          <p className="text-xs text-gray-500">Avg Confidence</p>
        </div>
      </div>

      {/* Most Common Disease */}
      <div className="card p-4 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center flex-shrink-0">
          <Bug className="w-5 h-5 text-amber-600" />
        </div>
        <div className="min-w-0">
          <p className="text-base font-bold text-agri-text leading-tight truncate">
            {mostCommon ? DISEASE_DISPLAY_NAMES[mostCommon[0] as keyof typeof DISEASE_DISPLAY_NAMES] : "None"}
          </p>
          <p className="text-xs text-gray-500">Most Common Disease</p>
        </div>
      </div>
    </div>
  );
}

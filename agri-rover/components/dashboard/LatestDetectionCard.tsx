"use client";

import Link from "next/link";
import { latestDetection } from "@/lib/mock-data";
import { DISEASE_DISPLAY_NAMES, SEVERITY_CONFIG, SYMPTOM_LABELS } from "@/lib/disease-info";
import { formatRelativeTime } from "@/lib/utils";
import { ArrowRight, MapPin, Clock, Target } from "lucide-react";

export default function LatestDetectionCard() {
  const det = latestDetection;
  const dr = det.detection_result;
  const disease = DISEASE_DISPLAY_NAMES[dr.disease_class];
  const sev = SEVERITY_CONFIG[dr.severity_class];
  const confidence = Math.round(dr.confidence * 100);

  return (
    <div className="card p-5 animate-fade-in-up vine-border">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">
            Latest Detection
          </p>
          <h3 className="text-xl font-bold text-agri-text">{disease}</h3>
          <p className="text-sm text-gray-500 italic mt-0.5">
            {dr.disease_class === "healthy" ? "Momordica charantia — healthy" : ""}
          </p>
        </div>
        <span
          className="px-3 py-1.5 rounded-full text-xs font-bold border"
          style={{ color: sev.color, backgroundColor: sev.bg, borderColor: sev.color + "40" }}
        >
          {sev.label}
        </span>
      </div>

      {/* Confidence bar */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-1.5">
          <span className="text-sm font-medium text-gray-600">AI Confidence</span>
          <span className="text-sm font-bold text-leaf">{confidence}%</span>
        </div>
        <div className="w-full h-3 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full bg-leaf-gradient transition-all duration-1000 ease-out animate-grow"
            style={{ width: `${confidence}%` }}
          />
        </div>
      </div>

      {/* Info row */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-green-50 rounded-xl p-3 text-center border border-green-100">
          <Target className="w-4 h-4 text-leaf mx-auto mb-1" />
          <p className="text-lg font-bold text-leaf">{dr.affected_area_percentage}%</p>
          <p className="text-[11px] text-gray-500">Affected Area</p>
        </div>
        <div className="bg-blue-50 rounded-xl p-3 text-center border border-blue-100">
          <MapPin className="w-4 h-4 text-sky mx-auto mb-1" />
          <p className="text-lg font-bold text-sky">R{det.rover_location.row}{det.rover_location.section}</p>
          <p className="text-[11px] text-gray-500">Location</p>
        </div>
        <div className="bg-gray-50 rounded-xl p-3 text-center border border-gray-100">
          <Clock className="w-4 h-4 text-gray-400 mx-auto mb-1" />
          <p className="text-sm font-bold text-gray-600">{formatRelativeTime(det.timestamp)}</p>
          <p className="text-[11px] text-gray-500">Detected</p>
        </div>
      </div>

      {/* Symptoms */}
      {dr.symptoms_detected.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">Symptoms Detected</p>
          <div className="flex flex-wrap gap-2">
            {dr.symptoms_detected.map((s) => (
              <span
                key={s}
                className="px-2.5 py-1 bg-amber-50 border border-amber-200 text-amber-700 text-xs font-medium rounded-full"
              >
                {SYMPTOM_LABELS[s] ?? s}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* CTA */}
      <Link
        href="/detection"
        className="flex items-center justify-center gap-2 w-full py-3 bg-leaf-gradient text-white rounded-xl font-semibold text-sm hover:opacity-90 transition-opacity shadow-glow group"
      >
        View Full Analysis
        <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
      </Link>
    </div>
  );
}

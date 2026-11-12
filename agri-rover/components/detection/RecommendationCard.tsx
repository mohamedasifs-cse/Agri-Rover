"use client";

import { CheckCircle2, Shield } from "lucide-react";

interface RecommendationCardProps {
  immediate: string[];
  preventive: string[];
  farmerSummary: string;
}

export default function RecommendationCard({ immediate, preventive, farmerSummary }: RecommendationCardProps) {
  return (
    <div className="space-y-4 animate-fade-in-up">
      {/* Farmer summary */}
      <div className="bg-leaf-gradient rounded-2xl p-4 text-white shadow-glow">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xl">🌾</span>
          <span className="font-semibold text-sm">AI Farmer Advice</span>
        </div>
        <p className="text-sm leading-relaxed opacity-95">{farmerSummary}</p>
      </div>

      {/* Immediate actions */}
      <div className="card p-4 border-l-4 border-danger">
        <div className="flex items-center gap-2 mb-3">
          <CheckCircle2 className="w-5 h-5 text-danger flex-shrink-0" />
          <h4 className="font-semibold text-agri-text">Immediate Actions</h4>
          <span className="ml-auto text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full font-semibold">
            Do Now
          </span>
        </div>
        <ol className="space-y-2">
          {immediate.map((action, i) => (
            <li key={i} className="flex items-start gap-3 text-sm">
              <span className="flex-shrink-0 w-5 h-5 rounded-full bg-red-100 text-red-600 text-xs font-bold flex items-center justify-center mt-0.5">
                {i + 1}
              </span>
              <span className="text-gray-700 leading-relaxed">{action}</span>
            </li>
          ))}
        </ol>
      </div>

      {/* Preventive measures */}
      <div className="card p-4 border-l-4 border-primary">
        <div className="flex items-center gap-2 mb-3">
          <Shield className="w-5 h-5 text-primary flex-shrink-0" />
          <h4 className="font-semibold text-agri-text">Prevention Tips</h4>
          <span className="ml-auto text-xs bg-green-100 text-green-600 px-2 py-0.5 rounded-full font-semibold">
            Long-term
          </span>
        </div>
        <ul className="space-y-2">
          {preventive.map((tip, i) => (
            <li key={i} className="flex items-start gap-3 text-sm">
              <span className="flex-shrink-0 text-primary mt-1">✓</span>
              <span className="text-gray-700 leading-relaxed">{tip}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

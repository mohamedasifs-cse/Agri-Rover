"use client";

import { latestDetection } from "@/lib/mock-data";
import { Thermometer, Droplets, Zap, Sun } from "lucide-react";

const sensors = [
  {
    key: "temperature_celsius" as const,
    label: "Temperature",
    unit: "°C",
    icon: Thermometer,
    color: "text-orange-500",
    bg: "bg-orange-50",
    border: "border-orange-200",
    barColor: "bg-gradient-to-r from-orange-300 to-orange-500",
    min: 20,
    max: 45,
    warning: (v: number) => v > 35 || v < 20,
    tip: (v: number) =>
      v > 35 ? "⚠️ High temp — risk of heat stress" : v < 20 ? "🌡️ Too cool for bitter gourd" : "✅ Ideal range",
  },
  {
    key: "humidity_percentage" as const,
    label: "Humidity",
    unit: "%",
    icon: Droplets,
    color: "text-blue-500",
    bg: "bg-blue-50",
    border: "border-blue-200",
    barColor: "bg-gradient-to-r from-blue-300 to-blue-500",
    min: 0,
    max: 100,
    warning: (v: number) => v > 80,
    tip: (v: number) => (v > 80 ? "⚠️ High humidity — fungal risk" : "✅ Acceptable"),
  },
  {
    key: "soil_moisture_percentage" as const,
    label: "Soil Moisture",
    unit: "%",
    icon: Zap,
    color: "text-emerald-600",
    bg: "bg-emerald-50",
    border: "border-emerald-200",
    barColor: "bg-gradient-to-r from-emerald-300 to-emerald-500",
    min: 0,
    max: 100,
    warning: (v: number) => v < 40 || v > 80,
    tip: (v: number) =>
      v < 40 ? "💧 Too dry — water your plants" : v > 80 ? "🌊 Waterlogged — reduce watering" : "✅ Good moisture",
  },
  {
    key: "light_intensity_lux" as const,
    label: "Light Intensity",
    unit: " lux",
    icon: Sun,
    color: "text-yellow-500",
    bg: "bg-yellow-50",
    border: "border-yellow-200",
    barColor: "bg-gradient-to-r from-yellow-300 to-yellow-500",
    min: 0,
    max: 2000,
    warning: (v: number) => v < 400,
    tip: (v: number) => (v < 400 ? "🌥️ Too little light" : "☀️ Good light level"),
  },
];

export default function EnvironmentPanel() {
  const env = latestDetection.environmental_data;

  return (
    <div className="card p-5 animate-fade-in-up">
      <div className="flex items-center gap-2 mb-5">
        <div className="w-8 h-8 rounded-lg bg-sky-100 flex items-center justify-center">
          <span className="text-sky-600 text-sm">🌡️</span>
        </div>
        <div>
          <h3 className="text-base font-semibold text-agri-text">Environmental Conditions</h3>
          <p className="text-xs text-gray-400">Live IoT sensor readings</p>
        </div>
      </div>

      <div className="space-y-4">
        {sensors.map(({ key, label, unit, icon: Icon, color, bg, border, barColor, min, max, warning, tip }) => {
          const value = env[key];
          const pct = Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100));
          const isWarning = warning(value);

          return (
            <div key={key} className={`rounded-xl p-3.5 ${bg} border ${border}`}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Icon className={`w-4 h-4 ${color}`} />
                  <span className="text-sm font-medium text-agri-text">{label}</span>
                </div>
                <div className="flex items-center gap-2">
                  {isWarning && (
                    <span className="text-[10px] bg-red-100 text-red-600 px-1.5 py-0.5 rounded-full font-semibold">
                      Alert
                    </span>
                  )}
                  <span className={`text-lg font-bold ${color}`}>
                    {key === "light_intensity_lux" ? value.toFixed(0) : value.toFixed(1)}
                    {unit}
                  </span>
                </div>
              </div>
              <div className="w-full h-2 bg-white/60 rounded-full overflow-hidden">
                <div
                  className={`h-full ${barColor} rounded-full transition-all duration-700 animate-grow`}
                  style={{ width: `${pct}%` }}
                />
              </div>
              <p className="text-[11px] text-gray-500 mt-1.5">{tip(value)}</p>
            </div>
          );
        })}
      </div>

      <p className="text-[11px] text-gray-400 mt-4 text-right">
        Updated: {new Date(latestDetection.timestamp).toLocaleTimeString("en-IN")}
      </p>
    </div>
  );
}

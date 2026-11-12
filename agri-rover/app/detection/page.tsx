import ConfidenceMeter from "@/components/detection/ConfidenceMeter";
import SeverityBadge from "@/components/detection/SeverityBadge";
import RecommendationCard from "@/components/detection/RecommendationCard";
import WebcamCaptureCard from "@/components/detection/WebcamCaptureCard";
import { latestDetection } from "@/lib/mock-data";
import { DISEASE_INFO, DISEASE_DISPLAY_NAMES, SYMPTOM_LABELS, SEVERITY_CONFIG } from "@/lib/disease-info";
import { formatTimestamp } from "@/lib/utils";
import { MapPin, Clock, Activity, Thermometer, Droplets, Zap, Sun } from "lucide-react";

export default function DetectionPage() {
  const det = latestDetection;
  const dr = det.detection_result;
  const info = DISEASE_INFO[dr.disease_class];
  const sev = SEVERITY_CONFIG[dr.severity_class];
  const displayName = DISEASE_DISPLAY_NAMES[dr.disease_class];

  return (
    <div className="space-y-6">
      {/* Real-time USB Webcam & AI Diagnosis Integration */}
      <WebcamCaptureCard />

      {/* Header card */}
      <div className="card p-6 bg-gradient-to-br from-white to-green-50">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">
              Detection ID: {det.id}
            </p>
            <h2 className="text-2xl font-bold text-agri-text">{displayName}</h2>
            <p className="text-sm text-gray-500 italic mt-1">{info.scientific_name}</p>
            <p className="text-base text-gray-600 mt-3 max-w-xl leading-relaxed">{info.description}</p>
          </div>
          <div className="flex flex-col items-center gap-4 md:items-end">
            <ConfidenceMeter confidence={dr.confidence} />
            <SeverityBadge severity={dr.severity_class} size="lg" showDescription />
          </div>
        </div>
      </div>

      {/* Detection stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card p-4 text-center">
          <div className="w-10 h-10 bg-red-100 rounded-xl flex items-center justify-center mx-auto mb-2">
            <Activity className="w-5 h-5 text-red-500" />
          </div>
          <p className="text-2xl font-bold text-agri-text">{dr.affected_area_percentage}%</p>
          <p className="text-xs text-gray-500 mt-0.5">Affected Area</p>
        </div>
        <div className="card p-4 text-center">
          <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center mx-auto mb-2">
            <MapPin className="w-5 h-5 text-sky" />
          </div>
          <p className="text-xl font-bold text-agri-text">R{det.rover_location.row} – {det.rover_location.section}</p>
          <p className="text-xs text-gray-500 mt-0.5">Location</p>
        </div>
        <div className="card p-4 text-center col-span-2">
          <div className="w-10 h-10 bg-gray-100 rounded-xl flex items-center justify-center mx-auto mb-2">
            <Clock className="w-5 h-5 text-gray-400" />
          </div>
          <p className="text-base font-bold text-agri-text">{formatTimestamp(det.timestamp)}</p>
          <p className="text-xs text-gray-500 mt-0.5">Detection Time</p>
        </div>
      </div>

      {/* Symptoms */}
      {dr.symptoms_detected.length > 0 && (
        <div className="card p-5">
          <h3 className="text-base font-semibold text-agri-text mb-3">🔎 Symptoms Detected</h3>
          <div className="flex flex-wrap gap-2">
            {dr.symptoms_detected.map((s) => (
              <span key={s} className="px-3 py-1.5 bg-amber-50 border border-amber-200 text-amber-700 text-sm font-medium rounded-full">
                {SYMPTOM_LABELS[s] ?? s}
              </span>
            ))}
          </div>
          <div className="mt-4">
            <p className="text-sm font-semibold text-gray-600 mb-2">All known symptoms of {displayName}:</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {info.symptoms.map((s) => (
                <div key={s} className="flex items-center gap-2 text-sm text-gray-600">
                  <span className="text-primary">•</span> {s}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Main content: Recommendations + Env */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recommendations */}
        <div className="lg:col-span-2">
          <h3 className="text-base font-semibold text-agri-text mb-3">🌱 AI Recommendations</h3>
          <RecommendationCard
            immediate={info.recommendations.immediate}
            preventive={info.recommendations.preventive}
            farmerSummary={info.farmer_summary}
          />
        </div>

        {/* Environmental data at detection */}
        <div className="card p-5">
          <h3 className="text-base font-semibold text-agri-text mb-4">🌡️ Conditions at Detection</h3>
          <div className="space-y-4">
            {[
              { label: "Temperature", value: `${det.environmental_data.temperature_celsius}°C`, icon: Thermometer, color: "text-orange-500", bg: "bg-orange-50" },
              { label: "Humidity", value: `${det.environmental_data.humidity_percentage}%`, icon: Droplets, color: "text-blue-500", bg: "bg-blue-50" },
              { label: "Soil Moisture", value: `${det.environmental_data.soil_moisture_percentage}%`, icon: Zap, color: "text-emerald-600", bg: "bg-emerald-50" },
              { label: "Light", value: `${det.environmental_data.light_intensity_lux} lux`, icon: Sun, color: "text-yellow-500", bg: "bg-yellow-50" },
            ].map(({ label, value, icon: Icon, color, bg }) => (
              <div key={label} className={`flex items-center gap-3 p-3 rounded-xl ${bg}`}>
                <Icon className={`w-4 h-4 ${color} flex-shrink-0`} />
                <span className="text-sm text-gray-600 flex-1">{label}</span>
                <span className={`text-sm font-bold ${color}`}>{value}</span>
              </div>
            ))}
          </div>

          {/* Causes */}
          <div className="mt-5 pt-4 border-t border-gray-100">
            <p className="text-sm font-semibold text-gray-600 mb-2">🔍 Disease Causes</p>
            <ul className="space-y-1.5">
              {info.causes.map((c) => (
                <li key={c} className="flex items-start gap-2 text-sm text-gray-600">
                  <span className="text-danger mt-0.5">▲</span> {c}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

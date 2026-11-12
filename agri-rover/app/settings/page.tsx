"use client";

import { useState } from "react";
import { Save, Download, Bell, MapPin, Crop, Ruler } from "lucide-react";

interface FarmProfile {
  farmName: string;
  location: string;
  cropType: string;
  pandalLength: string;
  pandalWidth: string;
  rows: string;
  sections: string;
  ownerName: string;
  phone: string;
}

export default function SettingsPage() {
  const [profile, setProfile] = useState<FarmProfile>({
    farmName: "Green Valley Bitter Gourd Farm",
    location: "Coimbatore, Tamil Nadu",
    cropType: "Bitter Gourd (Momordica charantia)",
    pandalLength: "50",
    pandalWidth: "20",
    rows: "5",
    sections: "4",
    ownerName: "Ravi Kumar",
    phone: "+91 98765 43210",
  });

  const [notifications, setNotifications] = useState({
    diseaseAlert: true,
    severeAlert: true,
    dailySummary: false,
    weeklyReport: true,
    weatherAlert: false,
  });

  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleExportCSV = () => {
    const rows = [
      ["ID", "Timestamp", "Disease", "Severity", "Confidence", "Affected %", "Row", "Section", "Temp", "Humidity"],
      ["det_001", "2026-09-11 14:30", "Powdery Mildew", "Moderate", "94%", "25%", "2", "B", "31°C", "78%"],
      ["det_002", "2026-09-10 09:15", "Downy Mildew", "Early", "87%", "12%", "4", "A", "28°C", "85%"],
      ["det_004", "2026-09-08 15:00", "Fungal Leaf Spot", "Severe", "91%", "65%", "3", "D", "33°C", "82%"],
      ["det_005", "2026-09-07 10:20", "Viral Symptoms", "Moderate", "79%", "38%", "5", "B", "30°C", "76%"],
    ];
    const csv = rows.map((r) => r.join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "agri-rover-detections.csv";
    a.click();
  };

  return (
    <div className="max-w-3xl space-y-6">
      {/* Farm Profile */}
      <div className="card p-6">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center">
            <MapPin className="w-5 h-5 text-leaf" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-agri-text">Farm Profile</h3>
            <p className="text-xs text-gray-400">Basic information about your farm</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            { label: "Farm Name", key: "farmName" as const, icon: "🌿" },
            { label: "Location", key: "location" as const, icon: "📍" },
            { label: "Owner Name", key: "ownerName" as const, icon: "👤" },
            { label: "Phone Number", key: "phone" as const, icon: "📱" },
          ].map(({ label, key, icon }) => (
            <div key={key}>
              <label className="block text-xs font-semibold text-gray-500 mb-1.5 uppercase tracking-wide">
                {icon} {label}
              </label>
              <input
                value={profile[key]}
                onChange={(e) => setProfile({ ...profile, [key]: e.target.value })}
                className="w-full px-4 py-2.5 bg-green-50 border border-green-200 rounded-xl text-sm text-agri-text focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
              />
            </div>
          ))}

          <div className="md:col-span-2">
            <label className="block text-xs font-semibold text-gray-500 mb-1.5 uppercase tracking-wide">
              🌱 Crop Type
            </label>
            <input
              value={profile.cropType}
              onChange={(e) => setProfile({ ...profile, cropType: e.target.value })}
              className="w-full px-4 py-2.5 bg-green-50 border border-green-200 rounded-xl text-sm text-agri-text focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
            />
          </div>
        </div>
      </div>

      {/* Pandal Dimensions */}
      <div className="card p-6">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
            <Ruler className="w-5 h-5 text-sky" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-agri-text">Pandal Dimensions</h3>
            <p className="text-xs text-gray-400">Physical layout of your pandal farm</p>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "Length (m)", key: "pandalLength" as const },
            { label: "Width (m)", key: "pandalWidth" as const },
            { label: "No. of Rows", key: "rows" as const },
            { label: "No. of Sections", key: "sections" as const },
          ].map(({ label, key }) => (
            <div key={key}>
              <label className="block text-xs font-semibold text-gray-500 mb-1.5 uppercase tracking-wide">
                {label}
              </label>
              <input
                type="number"
                value={profile[key]}
                onChange={(e) => setProfile({ ...profile, [key]: e.target.value })}
                className="w-full px-4 py-2.5 bg-blue-50 border border-blue-200 rounded-xl text-sm text-agri-text focus:outline-none focus:ring-2 focus:ring-sky/30 focus:border-sky"
              />
            </div>
          ))}
        </div>
      </div>

      {/* Notifications */}
      <div className="card p-6">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 bg-amber-100 rounded-xl flex items-center justify-center">
            <Bell className="w-5 h-5 text-warning" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-agri-text">Notification Preferences</h3>
            <p className="text-xs text-gray-400">Choose what alerts you want to receive</p>
          </div>
        </div>

        <div className="space-y-3">
          {[
            { key: "diseaseAlert" as const, label: "Disease Detection Alert", desc: "Notify when any disease is detected" },
            { key: "severeAlert" as const, label: "Severe Disease Alert", desc: "Urgent notification for severe cases" },
            { key: "dailySummary" as const, label: "Daily Farm Summary", desc: "End-of-day health summary report" },
            { key: "weeklyReport" as const, label: "Weekly Analysis Report", desc: "7-day trend and comparison report" },
            { key: "weatherAlert" as const, label: "Weather Risk Alert", desc: "Notify when conditions favor disease spread" },
          ].map(({ key, label, desc }) => (
            <div key={key} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-green-50 transition-colors">
              <div>
                <p className="text-sm font-medium text-agri-text">{label}</p>
                <p className="text-xs text-gray-400 mt-0.5">{desc}</p>
              </div>
              <button
                onClick={() => setNotifications({ ...notifications, [key]: !notifications[key] })}
                className={`relative w-12 h-6 rounded-full transition-colors duration-200 ${notifications[key] ? "bg-primary" : "bg-gray-300"}`}
              >
                <span
                  className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform duration-200 ${notifications[key] ? "translate-x-7" : "translate-x-1"}`}
                />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Data Export */}
      <div className="card p-6">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 bg-purple-100 rounded-xl flex items-center justify-center">
            <Download className="w-5 h-5 text-purple-500" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-agri-text">Data Export</h3>
            <p className="text-xs text-gray-400">Download your farm data for records</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-3 p-4 bg-green-50 border border-green-200 rounded-xl hover:bg-green-100 transition-colors group"
          >
            <Download className="w-5 h-5 text-leaf group-hover:scale-110 transition-transform" />
            <div className="text-left">
              <p className="text-sm font-semibold text-leaf">Download CSV</p>
              <p className="text-xs text-gray-500">Detection history spreadsheet</p>
            </div>
          </button>
          <button className="flex items-center gap-3 p-4 bg-purple-50 border border-purple-200 rounded-xl hover:bg-purple-100 transition-colors group opacity-60 cursor-not-allowed">
            <Download className="w-5 h-5 text-purple-500" />
            <div className="text-left">
              <p className="text-sm font-semibold text-purple-600">Download PDF Report</p>
              <p className="text-xs text-gray-500">Coming in Phase 4</p>
            </div>
          </button>
        </div>
      </div>

      {/* Save button */}
      <button
        onClick={handleSave}
        className={`w-full py-3.5 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 transition-all ${
          saved
            ? "bg-primary text-white shadow-glow"
            : "bg-leaf-gradient text-white shadow-card hover:opacity-90"
        }`}
      >
        <Save className="w-4 h-4" />
        {saved ? "✅ Settings Saved!" : "Save Settings"}
      </button>
    </div>
  );
}

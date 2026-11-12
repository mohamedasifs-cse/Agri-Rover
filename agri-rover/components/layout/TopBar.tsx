"use client";

import { Bell, Sun, Cloud, Thermometer } from "lucide-react";
import { latestDetection } from "@/lib/mock-data";

const pages: Record<string, { title: string; subtitle: string }> = {
  "/": { title: "Farm Dashboard", subtitle: "Real-time health overview of your pandal farm" },
  "/map": { title: "Farm Map", subtitle: "Interactive grid view of all plant locations" },
  "/detection": { title: "Disease Details", subtitle: "Latest AI detection analysis" },
  "/assistant": { title: "AI Assistant", subtitle: "Ask me anything about your farm" },
  "/history": { title: "History & Trends", subtitle: "Disease progression over time" },
  "/settings": { title: "Farm Settings", subtitle: "Configure your farm profile" },
};

interface TopBarProps {
  pathname: string;
}

export default function TopBar({ pathname }: TopBarProps) {
  const page = pages[pathname] ?? { title: "AgriRover", subtitle: "Bitter gourd farm monitor" };
  const env = latestDetection.environmental_data;
  const now = new Date();
  const timeStr = now.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: true });
  const dateStr = now.toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long" });

  return (
    <header className="sticky top-0 z-30 bg-white/80 backdrop-blur-md border-b border-green-100 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Page title */}
        <div>
          <h2 className="text-xl font-bold text-leaf-dark">{page.title}</h2>
          <p className="text-sm text-gray-500 mt-0.5">{page.subtitle}</p>
        </div>

        {/* Right section */}
        <div className="flex items-center gap-4">
          {/* Quick sensor strip */}
          <div className="hidden md:flex items-center gap-3 bg-green-50 border border-green-200 rounded-xl px-4 py-2">
            <div className="flex items-center gap-1.5 text-sm font-medium text-orange-600">
              <Thermometer className="w-4 h-4" />
              <span>{env.temperature_celsius}°C</span>
            </div>
            <div className="w-px h-4 bg-green-200" />
            <div className="flex items-center gap-1.5 text-sm font-medium text-blue-600">
              <Cloud className="w-4 h-4" />
              <span>{env.humidity_percentage}%</span>
            </div>
            <div className="w-px h-4 bg-green-200" />
            <div className="flex items-center gap-1.5 text-sm font-medium text-yellow-600">
              <Sun className="w-4 h-4" />
              <span>{env.light_intensity_lux} lux</span>
            </div>
          </div>

          {/* Date & time */}
          <div className="hidden md:block text-right">
            <p className="text-sm font-semibold text-leaf-dark">{timeStr}</p>
            <p className="text-xs text-gray-400">{dateStr}</p>
          </div>

          {/* Notification bell */}
          <button className="relative w-10 h-10 rounded-xl bg-red-50 border border-red-200 flex items-center justify-center hover:bg-red-100 transition-colors">
            <Bell className="w-5 h-5 text-red-500" />
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
              3
            </span>
          </button>
        </div>
      </div>
    </header>
  );
}

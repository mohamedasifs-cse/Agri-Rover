import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatTimestamp(ts: string): string {
  const d = new Date(ts);
  return d.toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  });
}

export function formatRelativeTime(ts: string): string {
  const diff = Date.now() - new Date(ts).getTime();
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  if (hours < 1) return "Just now";
  if (hours < 24) return `${hours}h ago`;
  return `${days}d ago`;
}

export function confidenceLabel(confidence: number): string {
  if (confidence >= 0.9) return "Very High";
  if (confidence >= 0.75) return "High";
  if (confidence >= 0.6) return "Moderate";
  return "Low";
}

export function getSectionColor(section: string): string {
  const colors: Record<string, string> = {
    A: "#3B82F6",
    B: "#8B5CF6",
    C: "#F59E0B",
    D: "#EF4444",
  };
  return colors[section] ?? "#6B7280";
}

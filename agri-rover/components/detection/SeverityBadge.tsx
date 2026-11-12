"use client";

import { SeverityClass } from "@/lib/mock-data";
import { SEVERITY_CONFIG } from "@/lib/disease-info";
import { cn } from "@/lib/utils";

interface SeverityBadgeProps {
  severity: SeverityClass;
  size?: "sm" | "md" | "lg";
  showDescription?: boolean;
}

export default function SeverityBadge({ severity, size = "md", showDescription = false }: SeverityBadgeProps) {
  const config = SEVERITY_CONFIG[severity];

  const sizeClasses = {
    sm: "px-2 py-0.5 text-xs",
    md: "px-3 py-1.5 text-sm",
    lg: "px-4 py-2 text-base",
  };

  return (
    <div className="inline-flex flex-col gap-1">
      <span
        className={cn(
          "inline-flex items-center gap-1.5 font-bold rounded-full border animate-scale-in",
          sizeClasses[size]
        )}
        style={{
          color: config.color,
          backgroundColor: config.bg,
          borderColor: config.color + "40",
        }}
      >
        <span
          className="w-2 h-2 rounded-full flex-shrink-0"
          style={{ backgroundColor: config.color }}
        />
        {config.label}
      </span>
      {showDescription && (
        <p className="text-xs text-gray-500 pl-1">{config.description}</p>
      )}
    </div>
  );
}

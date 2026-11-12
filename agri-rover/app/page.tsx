import HealthSummaryCards from "@/components/dashboard/HealthSummaryCards";
import EnvironmentPanel from "@/components/dashboard/EnvironmentPanel";
import LatestDetectionCard from "@/components/dashboard/LatestDetectionCard";
import QuickStatsBar from "@/components/dashboard/QuickStatsBar";
import FarmGrid from "@/components/map/FarmGrid";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* Health summary cards */}
      <HealthSummaryCards />

      {/* Quick stats bar */}
      <QuickStatsBar />

      {/* Main grid: Farm map (left 2/3) + right column stacks Env panel + Latest Detection */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <FarmGrid />
        </div>
        <div className="flex flex-col gap-6">
          <EnvironmentPanel />
          <LatestDetectionCard />
        </div>
      </div>
    </div>
  );
}

import FarmGrid from "@/components/map/FarmGrid";

export default function MapPage() {
  return (
    <div className="space-y-6">
      <div className="card p-5">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-2xl">🗺️</span>
          <div>
            <h2 className="text-xl font-bold text-agri-text">Pandal Farm Map</h2>
            <p className="text-sm text-gray-500">Interactive view of all plant locations — click any cell for details</p>
          </div>
        </div>

        {/* Section legend */}
        <div className="flex flex-wrap gap-3 mt-4">
          {["A", "B", "C", "D"].map((s, i) => {
            const colors = ["bg-blue-500", "bg-purple-500", "bg-amber-500", "bg-red-500"];
            return (
              <div key={s} className="flex items-center gap-2 px-3 py-1.5 bg-gray-50 rounded-lg border border-gray-200">
                <div className={`w-3 h-3 rounded ${colors[i]}`} />
                <span className="text-sm font-medium text-gray-600">Section {s}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Full map */}
      <FarmGrid />

      {/* Farm stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Total Cells", value: "20", icon: "🌿", sub: "5 rows × 4 sections" },
          { label: "Healthy", value: "12", icon: "🟢", sub: "60% of farm" },
          { label: "Need Attention", value: "4", icon: "🟡", sub: "Early symptoms" },
          { label: "Diseased", value: "4", icon: "🔴", sub: "Urgent action needed" },
        ].map(({ label, value, icon, sub }) => (
          <div key={label} className="card p-4 text-center">
            <p className="text-2xl mb-1">{icon}</p>
            <p className="text-2xl font-bold text-agri-text">{value}</p>
            <p className="text-sm font-medium text-gray-600">{label}</p>
            <p className="text-xs text-gray-400 mt-0.5">{sub}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

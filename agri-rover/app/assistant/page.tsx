import ChatInterface from "@/components/assistant/ChatInterface";
import { MessageCircle, Info } from "lucide-react";

export default function AssistantPage() {
  return (
    <div className="max-w-3xl mx-auto space-y-4">
      {/* Header */}
      <div className="card p-4 flex items-center gap-4 bg-leaf-gradient text-white shadow-glow">
        <div className="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center text-2xl flex-shrink-0">
          🌿
        </div>
        <div className="flex-1">
          <h2 className="text-lg font-bold">AgriRover AI Assistant</h2>
          <p className="text-sm text-white/80">Powered by disease detection data · Ask in any language</p>
        </div>
        <div className="flex items-center gap-1.5 bg-white/20 px-3 py-1.5 rounded-full">
          <span className="w-2 h-2 rounded-full bg-white animate-pulse" />
          <span className="text-xs font-semibold">Live</span>
        </div>
      </div>

      {/* Info banner */}
      <div className="flex items-start gap-3 bg-blue-50 border border-blue-200 rounded-xl p-3">
        <Info className="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" />
        <p className="text-xs text-blue-700">
          <strong>Tip:</strong> Ask me about disease name, how serious it is, where it was found, what to do, weather conditions, or detection history. I understand questions in simple language!
        </p>
      </div>

      {/* Chat box */}
      <div className="card overflow-hidden" style={{ height: "60vh", minHeight: 400 }}>
        <ChatInterface />
      </div>
    </div>
  );
}

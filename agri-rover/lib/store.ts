import { create } from "zustand";
import { DetectionResult, FarmCell, farmGrid, historicalDetections, latestDetection } from "./mock-data";

interface ChatMessage {
  id: string;
  role: "user" | "bot";
  content: string;
  timestamp: Date;
}

interface AgriStore {
  // Data
  detections: DetectionResult[];
  selectedDetection: DetectionResult | null;
  farmCells: FarmCell[];
  selectedCell: FarmCell | null;
  currentDetection: DetectionResult;

  // Chat
  chatMessages: ChatMessage[];

  // UI state
  isSidebarOpen: boolean;
  activeTab: string;

  // Actions
  setSelectedDetection: (d: DetectionResult | null) => void;
  setSelectedCell: (c: FarmCell | null) => void;
  addChatMessage: (msg: Omit<ChatMessage, "id" | "timestamp">) => void;
  clearChat: () => void;
  setSidebarOpen: (open: boolean) => void;
  setActiveTab: (tab: string) => void;
}

export const useAgriStore = create<AgriStore>((set) => ({
  detections: historicalDetections,
  selectedDetection: null,
  farmCells: farmGrid,
  selectedCell: null,
  currentDetection: latestDetection,

  chatMessages: [
    {
      id: "bot_welcome",
      role: "bot",
      content:
        "🌿 Hello! I'm your AgriRover AI Assistant. I can tell you about diseases on your farm, how serious they are, and what to do. How can I help you today?",
      timestamp: new Date(),
    },
  ],

  isSidebarOpen: false,
  activeTab: "dashboard",

  setSelectedDetection: (d) => set({ selectedDetection: d }),
  setSelectedCell: (c) => set({ selectedCell: c }),
  addChatMessage: (msg) =>
    set((state) => ({
      chatMessages: [
        ...state.chatMessages,
        { ...msg, id: `msg_${Date.now()}`, timestamp: new Date() },
      ],
    })),
  clearChat: () =>
    set({
      chatMessages: [
        {
          id: "bot_welcome",
          role: "bot",
          content:
            "🌿 Hello! I'm your AgriRover AI Assistant. I can tell you about diseases on your farm, how serious they are, and what to do. How can I help you today?",
          timestamp: new Date(),
        },
      ],
    }),
  setSidebarOpen: (open) => set({ isSidebarOpen: open }),
  setActiveTab: (tab) => set({ activeTab: tab }),
}));

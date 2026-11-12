"use client";

import { useState, useRef, useEffect } from "react";
import { Send, RefreshCw } from "lucide-react";

interface Message {
  id: string;
  role: "user" | "bot";
  content: string;
  timestamp: Date;
  context?: string;
}

const INITIAL_MESSAGES: Message[] = [
  {
    id: "welcome",
    role: "bot",
    content:
      "🌿 Hello! I'm your **AgriRover AI Assistant**.\n\nI'm watching over your bitter gourd pandal farm. The latest scan found **Powdery Mildew** in Row 2, Section B.\n\nWhat would you like to know?",
    timestamp: new Date(),
  },
];

const SUGGESTIONS = [
  "What disease was found?",
  "How serious is it?",
  "Where is the affected area?",
  "What should I do now?",
  "How is the weather?",
  "How to prevent it?",
];

function BotTypingIndicator() {
  return (
    <div className="flex items-end gap-2 animate-fade-in">
      <div className="w-8 h-8 rounded-full bg-leaf-gradient flex items-center justify-center text-white text-sm flex-shrink-0">
        🌿
      </div>
      <div className="chat-bubble-bot px-4 py-3">
        <div className="flex gap-1.5 items-center h-5">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="w-2 h-2 rounded-full bg-leaf animate-bounce"
              style={{ animationDelay: `${i * 150}ms` }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || isTyping) return;

    const userMsg: Message = {
      id: `user_${Date.now()}`,
      role: "user",
      content: text.trim(),
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    try {
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text.trim() }),
      });

      if (!res.ok) throw new Error("API error");

      const data = await res.json();
      const botMsg: Message = {
        id: `bot_${Date.now()}`,
        role: "bot",
        content: data.response,
        timestamp: new Date(),
        context: data.context_used,
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch {
      // Fallback if backend not running
      setMessages((prev) => [
        ...prev,
        {
          id: `bot_err_${Date.now()}`,
          role: "bot",
          content:
            "⚠️ Cannot connect to AgriRover backend. Please make sure the Python server is running:\n```\ncd backend\nuvicorn main:app --reload\n```",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  const clearChat = () => {
    setMessages(INITIAL_MESSAGES);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 p-4 pb-2">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-end gap-2 animate-fade-in-up ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}
          >
            {/* Avatar */}
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm flex-shrink-0 ${
                msg.role === "bot"
                  ? "bg-leaf-gradient text-white"
                  : "bg-sky text-white"
              }`}
            >
              {msg.role === "bot" ? "🌿" : "👨‍🌾"}
            </div>

            {/* Bubble */}
            <div className={`max-w-[78%] ${msg.role === "bot" ? "chat-bubble-bot" : "chat-bubble-user"} px-4 py-3`}>
              <div className="text-sm leading-relaxed whitespace-pre-wrap">
                {msg.content.split("\n").map((line, i) => (
                  <span key={i}>
                    {line.replace(/\*\*(.*?)\*\*/g, (_, t) => t)}
                    {i < msg.content.split("\n").length - 1 && <br />}
                  </span>
                ))}
              </div>
              <p className="text-[10px] opacity-50 mt-1.5 text-right">
                {msg.timestamp.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: true })}
              </p>
            </div>
          </div>
        ))}

        {isTyping && <BotTypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {/* Suggestions */}
      <div className="px-4 py-2">
        <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => sendMessage(s)}
              className="flex-shrink-0 px-3 py-1.5 bg-green-50 border border-green-200 text-green-700 text-xs font-medium rounded-full hover:bg-green-100 transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Input */}
      <div className="p-4 pt-2 border-t border-green-100">
        <form onSubmit={handleSubmit} className="flex items-center gap-2">
          <button
            type="button"
            onClick={clearChat}
            className="w-10 h-10 rounded-xl bg-gray-100 text-gray-500 flex items-center justify-center hover:bg-gray-200 transition-colors flex-shrink-0"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your farm... (e.g. What disease?)"
            className="flex-1 h-11 px-4 bg-green-50 border border-green-200 rounded-xl text-sm text-agri-text placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
          />
          <button
            type="submit"
            disabled={!input.trim() || isTyping}
            className="w-11 h-11 rounded-xl bg-leaf-gradient text-white flex items-center justify-center shadow-glow hover:opacity-90 transition-opacity disabled:opacity-50 flex-shrink-0"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}

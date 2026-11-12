"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Map,
  Bug,
  MessageCircle,
  History,
  Settings,
  Leaf,
  Wifi,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/map", label: "Farm Map", icon: Map },
  { href: "/detection", label: "Disease Details", icon: Bug },
  { href: "/assistant", label: "AI Assistant", icon: MessageCircle },
  { href: "/history", label: "History & Trends", icon: History },
  { href: "/settings", label: "Settings", icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden lg:flex flex-col w-64 min-h-screen bg-white border-r border-green-100 shadow-sm fixed top-0 left-0 z-40">
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-6 border-b border-green-100">
        <div className="w-10 h-10 rounded-xl bg-leaf-gradient flex items-center justify-center shadow-glow">
          <Leaf className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-leaf-dark tracking-tight">AgriRover</h1>
          <p className="text-xs text-gray-500 font-medium">Disease Monitor</p>
        </div>
      </div>

      {/* Live indicator */}
      <div className="mx-4 mt-4 px-4 py-2.5 bg-green-50 rounded-xl border border-green-200 flex items-center gap-2">
        <span className="relative flex h-2.5 w-2.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75" />
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-primary" />
        </span>
        <Wifi className="w-3.5 h-3.5 text-primary" />
        <span className="text-xs font-semibold text-primary">Rover Online</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "nav-item group",
                active ? "nav-item-active" : "nav-item-inactive"
              )}
            >
              <Icon className={cn("w-5 h-5 flex-shrink-0", active ? "text-white" : "text-leaf")} />
              <span>{label}</span>
              {active && (
                <span className="ml-auto w-1.5 h-1.5 rounded-full bg-white opacity-80" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-6 py-5 border-t border-green-100">
        <p className="text-xs text-gray-400 font-medium">Bitter Gourd Pandal Farm</p>
        <p className="text-xs text-gray-300 mt-1">5 Rows × 4 Sections</p>
        <p className="text-xs text-gray-300">Last scan: 2 hrs ago</p>
      </div>
    </aside>
  );
}

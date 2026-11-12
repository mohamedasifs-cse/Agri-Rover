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
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Home", icon: LayoutDashboard },
  { href: "/map", label: "Map", icon: Map },
  { href: "/detection", label: "Disease", icon: Bug },
  { href: "/assistant", label: "AI Chat", icon: MessageCircle },
  { href: "/history", label: "History", icon: History },
  { href: "/settings", label: "Settings", icon: Settings },
];

export default function MobileNav() {
  const pathname = usePathname();

  return (
    <nav className="lg:hidden fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-green-100 shadow-[0_-4px_20px_rgba(34,197,94,0.08)]">
      <div className="flex items-center justify-around px-2 py-2">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "mobile-nav-item",
                active
                  ? "text-primary bg-green-50"
                  : "text-gray-400 hover:text-leaf"
              )}
            >
              <Icon className={cn("w-5 h-5", active && "text-primary")} />
              <span className={cn("text-[10px]", active && "font-semibold text-primary")}>
                {label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}

"use client";

import { usePathname } from "next/navigation";
import TopBar from "./TopBar";

export default function TopBarWrapper() {
  const pathname = usePathname();
  return <TopBar pathname={pathname} />;
}

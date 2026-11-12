import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "@/components/layout/Sidebar";
import MobileNav from "@/components/layout/MobileNav";
import TopBarWrapper from "@/components/layout/TopBarWrapper";

export const metadata: Metadata = {
  title: "AgriRover – AI Disease Monitor for Bitter Gourd Farms",
  description:
    "Real-time AI-powered disease monitoring for bitter gourd pandal farms. Track plant health, detect diseases early, and get farmer-friendly AI recommendations.",
  keywords: "bitter gourd, disease detection, AI, farm monitoring, pandal, agriculture",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-agri-bg text-agri-text antialiased">
        <div className="flex min-h-screen">
          {/* Desktop Sidebar */}
          <Sidebar />

          {/* Main content */}
          <main className="flex-1 lg:ml-64 flex flex-col min-h-screen">
            <TopBarWrapper />
            <div className="flex-1 p-4 md:p-6 pb-24 lg:pb-6 animate-fade-in">
              {children}
            </div>
          </main>
        </div>

        {/* Mobile Bottom Nav */}
        <MobileNav />
      </body>
    </html>
  );
}

import type { Metadata } from "next";

import "@/app/globals.css";
import { FooterRail } from "@/components/footer-rail";
import { SiteHeader } from "@/components/site-header";

export const metadata: Metadata = {
  title: "Skeptik",
  description: "An AI-native autonomous newsroom"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen font-sans">
        <SiteHeader />
        {children}
        <FooterRail />
      </body>
    </html>
  );
}

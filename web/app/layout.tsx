import type { Metadata } from "next";
import Navbar from "@/components/Navbar";
import "./globals.css";

export const metadata: Metadata = {
  title: "Optipoint — AI Location Intelligence",
  description: "Find optimal places to live using NLP, geospatial data, and ML.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 max-w-6xl w-full mx-auto px-4 py-8">{children}</main>
        <footer className="border-t border-slate-200 py-6 text-center text-sm text-slate-500">
          Optipoint · Built with FastAPI, spaCy, scikit-learn, Next.js, Leaflet
        </footer>
      </body>
    </html>
  );
}

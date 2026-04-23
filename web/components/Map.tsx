"use client";

import dynamic from "next/dynamic";

const Map = dynamic(() => import("./MapView"), {
  ssr: false,
  loading: () => (
    <div className="h-96 w-full rounded-lg bg-slate-100 animate-pulse flex items-center justify-center text-slate-400">
      Loading map…
    </div>
  ),
});

export default Map;
export type { MapMarker } from "./MapView";

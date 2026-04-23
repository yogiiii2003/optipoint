"use client";

import { useEffect, useRef } from "react";
import L from "leaflet";

L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

const originIcon = L.icon({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  className: "hue-rotate-[140deg]",
});

export type MapMarker = {
  lat: number;
  lon: number;
  label: string;
  kind?: "origin" | "result";
};

type Props = {
  center: { lat: number; lon: number };
  markers: MapMarker[];
  zoom?: number;
  className?: string;
};

export default function MapView({ center, markers, zoom = 13, className }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const markerLayerRef = useRef<L.LayerGroup | null>(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = L.map(containerRef.current, {
      center: [center.lat, center.lon],
      zoom,
      scrollWheelZoom: true,
    });
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(map);

    mapRef.current = map;
    markerLayerRef.current = L.layerGroup().addTo(map);

    return () => {
      try {
        markerLayerRef.current?.clearLayers();
        markerLayerRef.current = null;
        mapRef.current?.remove();
      } catch {
        // tolerate double-unmount in React 18 dev mode
      }
      mapRef.current = null;
    };
    // intentionally only on mount — props handled in the effect below
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    const layer = markerLayerRef.current;
    if (!map || !layer) return;

    map.setView([center.lat, center.lon], zoom);
    layer.clearLayers();

    for (const m of markers) {
      const marker =
        m.kind === "origin"
          ? L.marker([m.lat, m.lon], { icon: originIcon })
          : L.marker([m.lat, m.lon]);
      marker.bindPopup(m.label);
      layer.addLayer(marker);
    }
  }, [center.lat, center.lon, zoom, markers]);

  return <div ref={containerRef} className={className ?? "h-96 w-full"} />;
}

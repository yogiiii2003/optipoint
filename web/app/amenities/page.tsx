"use client";

import { useState } from "react";
import Map, { type MapMarker } from "@/components/Map";
import Spinner from "@/components/Spinner";
import { api } from "@/lib/api";
import {
  AMENITY_TYPES,
  prettyLabel,
  type AmenitySearchResponse,
  type AmenityType,
} from "@/lib/types";

export default function AmenitiesPage() {
  const [location, setLocation] = useState("Pune");
  const [amenityType, setAmenityType] = useState<AmenityType>("hospital");
  const [radius, setRadius] = useState(3000);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<AmenitySearchResponse | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await api.findAmenities(location, amenityType, radius);
      setData(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  const markers: MapMarker[] = data
    ? [
        { ...data.origin, label: `${location}`, kind: "origin" },
        ...data.amenities.map((a) => ({
          lat: a.lat,
          lon: a.lon,
          label: `${a.name} · ${a.distance_km} km`,
          kind: "result" as const,
        })),
      ]
    : [];

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold">Amenity Finder</h1>
        <p className="text-slate-600 mt-1">
          Find the nearest amenities of a specific type around any location.
        </p>
      </header>

      <form onSubmit={onSubmit} className="bg-white rounded-xl border border-slate-200 p-5 grid gap-4 sm:grid-cols-3">
        <label className="block sm:col-span-2">
          <span className="text-sm font-medium">Location</span>
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2"
            required
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium">Amenity</span>
          <select
            value={amenityType}
            onChange={(e) => setAmenityType(e.target.value as AmenityType)}
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2"
          >
            {AMENITY_TYPES.map((t) => (
              <option key={t} value={t}>
                {prettyLabel(t)}
              </option>
            ))}
          </select>
        </label>
        <label className="block sm:col-span-2">
          <span className="text-sm font-medium">Radius: {radius} m</span>
          <input
            type="range"
            min={500}
            max={30000}
            step={500}
            value={radius}
            onChange={(e) => setRadius(Number(e.target.value))}
            className="mt-1 w-full"
          />
        </label>
        <button
          type="submit"
          disabled={loading}
          className="sm:col-span-1 bg-brand-500 hover:bg-brand-600 disabled:opacity-60 text-white font-medium px-4 py-2 rounded-md transition self-end"
        >
          {loading ? "Searching…" : "Search"}
        </button>
      </form>

      {loading && <Spinner />}
      {error && (
        <div className="rounded-md bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm">
          {error}
        </div>
      )}

      {data && (
        <div className="grid gap-6 lg:grid-cols-2">
          <div>
            <h2 className="font-semibold mb-3">
              {data.amenities.length} {prettyLabel(amenityType)} found
            </h2>
            <ul className="space-y-2 max-h-[600px] overflow-y-auto pr-2">
              {data.amenities.map((a, i) => (
                <li
                  key={i}
                  className="bg-white border border-slate-200 rounded-lg p-3 text-sm flex justify-between"
                >
                  <span className="font-medium">{a.name}</span>
                  <span className="text-xs text-slate-500">{a.distance_km} km</span>
                </li>
              ))}
              {data.amenities.length === 0 && (
                <li className="text-sm text-slate-500">No matches in this radius.</li>
              )}
            </ul>
          </div>
          <div className="lg:sticky lg:top-20 h-[600px]">
            <Map center={data.origin} markers={markers} zoom={13} className="h-full w-full" />
          </div>
        </div>
      )}
    </div>
  );
}

"use client";

import { useState } from "react";
import Map, { type MapMarker } from "@/components/Map";
import Spinner from "@/components/Spinner";
import { api } from "@/lib/api";
import { prettyLabel, type ApartmentSearchResponse } from "@/lib/types";

export default function ApartmentsPage() {
  const [query, setQuery] = useState("apartment near hospital and supermarket in Pune");
  const [radius, setRadius] = useState(1500);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<ApartmentSearchResponse | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await api.searchApartments(query, radius);
      setData(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  const markers: MapMarker[] = data
    ? [
        { ...data.origin, label: "Search origin", kind: "origin" },
        ...data.apartments.slice(0, 20).map((a) => ({
          lat: a.lat,
          lon: a.lon,
          label: `${a.name} · score ${a.score.toFixed(4)}`,
          kind: "result" as const,
        })),
      ]
    : [];

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold">Apartment Finder</h1>
        <p className="text-slate-600 mt-1">
          Describe your ideal apartment location in plain English.
        </p>
      </header>

      <form onSubmit={onSubmit} className="bg-white rounded-xl border border-slate-200 p-5 space-y-4">
        <label className="block">
          <span className="text-sm font-medium">Query</span>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
            placeholder="apartment near hospital and supermarket in Pune"
            required
            minLength={3}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium">Search radius: {radius} m</span>
          <input
            type="range"
            min={500}
            max={5000}
            step={100}
            value={radius}
            onChange={(e) => setRadius(Number(e.target.value))}
            className="mt-1 w-full"
          />
        </label>
        <button
          type="submit"
          disabled={loading}
          className="bg-brand-500 hover:bg-brand-600 disabled:opacity-60 text-white font-medium px-4 py-2 rounded-md transition"
        >
          {loading ? "Searching…" : "Search"}
        </button>
      </form>

      {loading && <Spinner label="Querying Overpass · this can take 10-30s on first run" />}
      {error && (
        <div className="rounded-md bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm">
          {error}
        </div>
      )}

      {data && (
        <div className="grid gap-6 lg:grid-cols-2">
          <div>
            <h2 className="font-semibold mb-3">
              {data.apartments.length} results
            </h2>
            <ul className="space-y-2 max-h-[600px] overflow-y-auto pr-2">
              {data.apartments.map((a, i) => (
                <li
                  key={i}
                  className="bg-white border border-slate-200 rounded-lg p-4 text-sm"
                >
                  <div className="flex justify-between items-start gap-2">
                    <span className="font-medium">{a.name}</span>
                    <span className="shrink-0 text-xs bg-brand-50 text-brand-700 px-2 py-0.5 rounded">
                      score {a.score.toFixed(4)}
                    </span>
                  </div>
                  <div className="text-slate-500 text-xs mt-1">
                    {a.distance_km.toFixed(2)} km from origin
                  </div>
                  {Object.keys(a.nearest_amenities).length > 0 && (
                    <details className="mt-2">
                      <summary className="cursor-pointer text-xs text-slate-600">
                        Nearest amenities
                      </summary>
                      <ul className="mt-2 grid grid-cols-2 gap-1 text-xs text-slate-600">
                        {Object.entries(a.nearest_amenities).map(([cat, v]) => (
                          <li key={cat}>
                            <span className="text-slate-400">{prettyLabel(cat)}:</span>{" "}
                            {v.distance_km.toFixed(2)} km
                          </li>
                        ))}
                      </ul>
                    </details>
                  )}
                </li>
              ))}
            </ul>
          </div>
          <div className="lg:sticky lg:top-20 h-[600px]">
            <Map
              center={data.origin}
              markers={markers}
              zoom={14}
              className="h-full w-full"
            />
          </div>
        </div>
      )}
    </div>
  );
}

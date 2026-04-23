"use client";

import { useState } from "react";
import Map, { type MapMarker } from "@/components/Map";
import Spinner from "@/components/Spinner";
import { api } from "@/lib/api";
import { prettyLabel, type OptimalityResponse } from "@/lib/types";

export default function OptimalityPage() {
  const [location, setLocation] = useState("Jadavpur University");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<OptimalityResponse | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await api.predictOptimality(location);
      setData(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  const verdictColor =
    data?.verdict === "Optimal"
      ? "bg-green-50 border-green-200 text-green-800"
      : "bg-amber-50 border-amber-200 text-amber-800";

  const markers: MapMarker[] = data
    ? [{ ...data.origin, label: location, kind: "origin" }]
    : [];

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold">Optimality Predictor</h1>
        <p className="text-slate-600 mt-1">
          An sklearn ensemble decides whether a location is Optimal based on distances to 16 amenity categories.
        </p>
      </header>

      <form onSubmit={onSubmit} className="bg-white rounded-xl border border-slate-200 p-5 flex gap-3">
        <input
          type="text"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          className="flex-1 rounded-md border border-slate-300 px-3 py-2"
          placeholder="e.g. Jadavpur University"
          required
          minLength={2}
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-brand-500 hover:bg-brand-600 disabled:opacity-60 text-white font-medium px-4 py-2 rounded-md transition"
        >
          {loading ? "Predicting…" : "Predict"}
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
          <div className="space-y-4">
            <div className={`rounded-xl border p-5 ${verdictColor}`}>
              <div className="text-sm uppercase tracking-wide opacity-70">Verdict</div>
              <div className="text-3xl font-bold mt-1">{data.verdict}</div>
              {data.confidence !== null && (
                <div className="text-sm mt-2 opacity-80">
                  Confidence: {(data.confidence * 100).toFixed(1)}%
                </div>
              )}
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-5">
              <h3 className="font-semibold mb-3">Distances to nearest amenities</h3>
              <ul className="grid grid-cols-2 gap-y-2 gap-x-4 text-sm">
                {Object.entries(data.distances)
                  .sort((a, b) => a[1] - b[1])
                  .map(([cat, d]) => (
                    <li key={cat} className="flex justify-between">
                      <span className="text-slate-600">{prettyLabel(cat)}</span>
                      <span className="font-medium">
                        {d >= 99999 ? "—" : `${d.toFixed(2)} km`}
                      </span>
                    </li>
                  ))}
              </ul>
            </div>
          </div>
          <div className="h-[600px]">
            <Map center={data.origin} markers={markers} zoom={14} className="h-full w-full" />
          </div>
        </div>
      )}
    </div>
  );
}

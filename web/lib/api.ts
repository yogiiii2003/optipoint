import type {
  AmenitySearchResponse,
  ApartmentSearchResponse,
  OptimalityResponse,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function post<T>(path: string, body: unknown): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch (e) {
    throw new Error(
      `Cannot reach backend at ${API_URL} — is the API running? (${
        e instanceof Error ? e.message : "network error"
      })`
    );
  }
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const err = await res.json();
      if (err.detail) detail = typeof err.detail === "string" ? err.detail : JSON.stringify(err.detail);
    } catch {}
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export const api = {
  searchApartments: (query: string, radius_m: number) =>
    post<ApartmentSearchResponse>("/api/apartments/search", { query, radius_m }),

  findAmenities: (location: string, amenity_type: string, radius_m: number) =>
    post<AmenitySearchResponse>("/api/amenities/nearby", {
      location,
      amenity_type,
      radius_m,
    }),

  predictOptimality: (location: string) =>
    post<OptimalityResponse>("/api/optimality/predict", { location }),
};

export type LatLon = { lat: number; lon: number };

export type NearestAmenity = { name: string; distance_km: number };

export type ApartmentResult = {
  name: string;
  lat: number;
  lon: number;
  distance_km: number;
  score: number;
  nearest_amenities: Record<string, NearestAmenity>;
};

export type ApartmentSearchResponse = {
  origin: LatLon;
  apartments: ApartmentResult[];
};

export type Amenity = {
  name: string;
  lat: number;
  lon: number;
  distance_km: number;
};

export type AmenitySearchResponse = {
  origin: LatLon;
  amenities: Amenity[];
};

export type OptimalityResponse = {
  verdict: "Optimal" | "Not Optimal";
  confidence: number | null;
  origin: LatLon;
  distances: Record<string, number>;
};

export const AMENITY_TYPES = [
  "bus_stop",
  "train_station",
  "restaurant",
  "cafe",
  "supermarket",
  "park",
  "hospital",
  "pharmacy",
  "police_station",
  "fire_station",
  "school",
  "university",
  "library",
  "shopping_mall",
  "movie_theater",
  "museum",
] as const;

export type AmenityType = (typeof AMENITY_TYPES)[number];

export function prettyLabel(key: string): string {
  return key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

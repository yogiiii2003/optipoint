from __future__ import annotations

from fastapi import APIRouter, HTTPException
from geopy.distance import geodesic

from app.schemas import (
    ApartmentResult,
    ApartmentSearchRequest,
    ApartmentSearchResponse,
    LatLon,
    NearestAmenity,
)
from app.services import geocoding, nlp, overpass, scoring

_NEAREST_SEARCH_RADIUS_M = 15_000

router = APIRouter()


@router.post("/search", response_model=ApartmentSearchResponse)
async def search(req: ApartmentSearchRequest) -> ApartmentSearchResponse:
    locations = nlp.extract_location(req.query)
    if not locations:
        raise HTTPException(status_code=400, detail="No location found in query")
    coords = geocoding.geocode(" ".join(locations))
    if coords is None:
        raise HTTPException(
            status_code=404, detail=f"Location not found: {' '.join(locations)}"
        )
    lat, lon = coords

    weights, _ = nlp.extract_preferences(req.query)

    apartments = await overpass.nearby_apartments(lat, lon, req.radius_m)
    if not apartments:
        return ApartmentSearchResponse(origin=LatLon(lat=lat, lon=lon), apartments=[])

    # Optimization: query each category once centered at origin with a wide radius,
    # then compute nearest-to-each-apartment from that shared result set.
    # Collapses 16 * N Overpass calls into 16, since apartments are all within
    # req.radius_m of the origin and _NEAREST_SEARCH_RADIUS_M covers far beyond that.
    origin_cat_data = await overpass.query_all_categories(
        lat, lon, _NEAREST_SEARCH_RADIUS_M
    )

    results: list[ApartmentResult] = []
    for apt in apartments:
        distances: dict[str, float] = {}
        nearest_map: dict[str, NearestAmenity] = {}
        for cat, elements in origin_cat_data.items():
            n = overpass.nearest(apt["lat"], apt["lon"], elements)
            if n is not None:
                distances[cat] = n["distance_km"]
                nearest_map[cat] = NearestAmenity(
                    name=n["name"], distance_km=round(n["distance_km"], 2)
                )

        score = scoring.weighted_score(distances, weights)
        results.append(
            ApartmentResult(
                name=apt["name"],
                lat=apt["lat"],
                lon=apt["lon"],
                distance_km=round(
                    geodesic((lat, lon), (apt["lat"], apt["lon"])).kilometers, 2
                ),
                score=round(score, 6),
                nearest_amenities=nearest_map,
            )
        )

    results.sort(key=lambda r: r.score, reverse=True)
    return ApartmentSearchResponse(origin=LatLon(lat=lat, lon=lon), apartments=results)

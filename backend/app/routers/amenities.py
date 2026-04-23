from __future__ import annotations

from fastapi import APIRouter, HTTPException
from geopy.distance import geodesic

from app.schemas import Amenity, AmenitySearchRequest, AmenitySearchResponse, LatLon
from app.services import geocoding, overpass

router = APIRouter()


@router.post("/nearby", response_model=AmenitySearchResponse)
async def nearby(req: AmenitySearchRequest) -> AmenitySearchResponse:
    if req.amenity_type not in overpass.CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown amenity type '{req.amenity_type}'. "
            f"Supported: {sorted(overpass.CATEGORIES.keys())}",
        )

    coords = geocoding.geocode(req.location)
    if coords is None:
        raise HTTPException(status_code=404, detail=f"Location '{req.location}' not found")
    lat, lon = coords

    elements = await overpass.query_category(req.amenity_type, lat, lon, req.radius_m)
    amenities = [
        Amenity(
            name=e["name"],
            lat=e["lat"],
            lon=e["lon"],
            distance_km=round(geodesic((lat, lon), (e["lat"], e["lon"])).kilometers, 2),
        )
        for e in elements
    ]
    amenities.sort(key=lambda a: a.distance_km)
    return AmenitySearchResponse(origin=LatLon(lat=lat, lon=lon), amenities=amenities)

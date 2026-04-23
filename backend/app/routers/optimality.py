from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.ml import predict as ml_predict
from app.schemas import LatLon, OptimalityRequest, OptimalityResponse
from app.services import geocoding, overpass

_CATEGORY_SEARCH_RADIUS_M = 10_000
_MISSING_DISTANCE_KM = 100_000.0

router = APIRouter()


@router.post("/predict", response_model=OptimalityResponse)
async def predict(req: OptimalityRequest) -> OptimalityResponse:
    coords = geocoding.geocode(req.location)
    if coords is None:
        raise HTTPException(status_code=404, detail=f"Location '{req.location}' not found")
    lat, lon = coords

    cat_data = await overpass.query_all_categories(lat, lon, _CATEGORY_SEARCH_RADIUS_M)
    distances: dict[str, float] = {}
    for cat, elements in cat_data.items():
        n = overpass.nearest(lat, lon, elements)
        distances[cat] = n["distance_km"] if n is not None else _MISSING_DISTANCE_KM

    try:
        verdict, confidence = ml_predict.classify(distances)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e

    return OptimalityResponse(
        verdict=verdict,
        confidence=round(confidence, 3),
        origin=LatLon(lat=lat, lon=lon),
        distances={k: round(v, 2) for k, v in distances.items()},
    )

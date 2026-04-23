"""Geoapify Places provider — reliable commercial frontend for OSM POI data.

Free tier: 3000 requests/day. See https://www.geoapify.com/places-api
"""
from __future__ import annotations

import logging
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_PLACES_URL = "https://api.geoapify.com/v2/places"
_TIMEOUT_S = 20.0
_DEFAULT_LIMIT = 50

# Map our internal category names to Geoapify category strings.
# Docs: https://apidocs.geoapify.com/docs/places/#categories
CATEGORY_MAP: dict[str, str] = {
    "bus_stop": "public_transport.bus",
    "train_station": "public_transport.train",
    "restaurant": "catering.restaurant",
    "cafe": "catering.cafe",
    "supermarket": "commercial.supermarket",
    "park": "leisure.park",
    "hospital": "healthcare.hospital",
    "pharmacy": "healthcare.pharmacy",
    "police_station": "service.police",
    "fire_station": "service.fire_station",
    "school": "education.school",
    "university": "education.university",
    "library": "education.library",
    "shopping_mall": "commercial.shopping_mall",
    "movie_theater": "entertainment.cinema",
    "museum": "entertainment.museum",
}

# Categories used for the "apartment finder" — Geoapify doesn't index residential
# buildings like raw OSM does, so we use accommodation subtypes which behave similarly.
_APARTMENT_CATEGORIES = [
    "accommodation.hotel",
    "accommodation.hostel",
    "accommodation.guest_house",
    "accommodation.apartment",
    "accommodation.motel",
]


def is_configured() -> bool:
    return bool(settings.geoapify_api_key)


def _to_elements(features: list[dict]) -> list[dict]:
    """Convert Geoapify GeoJSON features → OSM-shaped elements our code already handles."""
    out = []
    for f in features:
        coords = f.get("geometry", {}).get("coordinates")
        if not coords or len(coords) < 2:
            continue
        lon, lat = coords[0], coords[1]
        props = f.get("properties", {}) or {}
        name = (
            props.get("name")
            or props.get("address_line1")
            or props.get("street")
            or f"Unnamed (id: {props.get('place_id', '?')})"
        )
        out.append(
            {
                "id": props.get("place_id"),
                "lat": lat,
                "lon": lon,
                "tags": {"name": name},
            }
        )
    return out


async def _fetch(categories: str, lat: float, lon: float, radius_m: int) -> list[dict]:
    params = {
        "categories": categories,
        "filter": f"circle:{lon},{lat},{radius_m}",
        "limit": _DEFAULT_LIMIT,
        "apiKey": settings.geoapify_api_key,
    }
    async with httpx.AsyncClient(timeout=_TIMEOUT_S) as client:
        resp = await client.get(_PLACES_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
    return _to_elements(data.get("features", []))


async def query_category(
    category: str, lat: float, lon: float, radius_m: int
) -> Optional[list[dict]]:
    if not is_configured():
        return None
    gcat = CATEGORY_MAP.get(category)
    if gcat is None:
        logger.debug("no Geoapify mapping for category '%s'", category)
        return None
    return await _fetch(gcat, lat, lon, radius_m)


async def nearby_apartments(
    lat: float, lon: float, radius_m: int
) -> Optional[list[dict]]:
    if not is_configured():
        return None
    return await _fetch(",".join(_APARTMENT_CATEGORIES), lat, lon, radius_m)

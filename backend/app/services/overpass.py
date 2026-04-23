from __future__ import annotations

import asyncio
import json
import logging
from typing import Optional

import httpx
from geopy.distance import geodesic

from app.config import settings
from app.services.demo import fixture_for_query
from app.services import geoapify

logger = logging.getLogger(__name__)

CATEGORIES: dict[str, str] = {
    "bus_stop": 'node["highway"="bus_stop"]',
    "train_station": 'node["railway"="station"]',
    "restaurant": 'node["amenity"="restaurant"]',
    "cafe": 'node["amenity"="cafe"]',
    "supermarket": 'node["shop"="supermarket"]',
    "park": 'node["leisure"="park"]',
    "hospital": 'node["amenity"="hospital"]',
    "pharmacy": 'node["amenity"="pharmacy"]',
    "police_station": 'node["amenity"="police"]',
    "fire_station": 'node["amenity"="fire_station"]',
    "school": 'node["amenity"="school"]',
    "university": 'node["amenity"="university"]',
    "library": 'node["amenity"="library"]',
    "shopping_mall": 'node["shop"="mall"]',
    "movie_theater": 'node["amenity"="cinema"]',
    "museum": 'node["tourism"="museum"]',
}

_APARTMENT_TAGS = [
    ("building", "apartments"),
    ("building", "house"),
    ("building", "dormitory"),
    ("tourism", "hotel"),
    ("tourism", "hostel"),
    ("tourism", "apartment"),
    ("amenity", "vacation_rental"),
    ("amenity", "guesthouse"),
]

_MAX_CONCURRENT_OVERPASS = 4

_redis = None  # type: ignore[var-annotated]
_redis_checked = False


async def _get_redis():
    global _redis, _redis_checked
    if _redis_checked:
        return _redis
    _redis_checked = True
    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url(settings.redis_url, decode_responses=True, socket_timeout=2)
        await client.ping()
        _redis = client
        logger.info("Redis cache enabled at %s", settings.redis_url)
    except Exception as e:
        logger.warning("Redis unavailable, running without cache: %s", e)
        _redis = None
    return _redis


async def _fetch_with_failover(query: str) -> list[dict]:
    headers = {"User-Agent": settings.nominatim_user_agent}
    last_error: Exception | None = None
    async with httpx.AsyncClient(
        timeout=settings.overpass_timeout_seconds, headers=headers
    ) as client:
        for url in settings.overpass_urls:
            for attempt in range(settings.overpass_max_retries + 1):
                try:
                    # POST with form body — avoids URL length limits on long queries
                    resp = await client.post(url, data={"data": query})
                    if resp.status_code in (429, 502, 503, 504):
                        raise httpx.HTTPStatusError(
                            f"Overpass {resp.status_code}", request=resp.request, response=resp
                        )
                    resp.raise_for_status()
                    return resp.json().get("elements", [])
                except (httpx.ConnectError, httpx.ReadTimeout, httpx.HTTPStatusError) as e:
                    last_error = e
                    backoff = 0.5 * (2**attempt)
                    logger.warning(
                        "Overpass %s (attempt %d/%d) failed: %s — retrying in %.1fs",
                        url, attempt + 1, settings.overpass_max_retries + 1, e, backoff,
                    )
                    await asyncio.sleep(backoff)
    assert last_error is not None
    raise last_error


async def _fetch(query: str, cache_key: str) -> list[dict]:
    if settings.demo_mode:
        return fixture_for_query(query)

    r = await _get_redis()
    if r is not None:
        try:
            cached = await r.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning("cache read failed: %s", e)

    try:
        elements = await _fetch_with_failover(query)
    except Exception as e:
        logger.warning("All Overpass mirrors failed (%s) — serving demo fixture", e)
        return fixture_for_query(query)

    if r is not None:
        try:
            await r.setex(cache_key, settings.cache_ttl_seconds, json.dumps(elements))
        except Exception as e:
            logger.warning("cache write failed: %s", e)

    return elements


def _normalize(elements: list[dict]) -> list[dict]:
    out = []
    for el in elements:
        if "lat" in el and "lon" in el:
            lat, lon = el["lat"], el["lon"]
        elif "center" in el:
            lat, lon = el["center"]["lat"], el["center"]["lon"]
        else:
            continue
        name = el.get("tags", {}).get("name") or f"Unnamed (ID: {el.get('id', '?')})"
        out.append({"lat": lat, "lon": lon, "name": name, "id": el.get("id")})
    return out


async def query_category(
    category: str, lat: float, lon: float, radius_m: int
) -> list[dict]:
    # Provider order: Geoapify (if configured) → Overpass → fixture fallback
    if geoapify.is_configured() and not settings.demo_mode:
        try:
            result = await geoapify.query_category(category, lat, lon, radius_m)
            if result is not None:
                return _normalize(result)
        except Exception as e:
            logger.warning("Geoapify query_category(%s) failed: %s — falling back", category, e)

    filter_expr = CATEGORIES[category]
    query = f"[out:json];{filter_expr}(around:{radius_m},{lat},{lon});out;"
    key = f"overpass:cat:{category}:{lat:.4f}:{lon:.4f}:{radius_m}"
    return _normalize(await _fetch(query, key))


async def query_all_categories(
    lat: float, lon: float, radius_m: int
) -> dict[str, list[dict]]:
    sem = asyncio.Semaphore(_MAX_CONCURRENT_OVERPASS)

    async def _bounded(cat: str) -> list[dict]:
        async with sem:
            return await query_category(cat, lat, lon, radius_m)

    tasks = [_bounded(cat) for cat in CATEGORIES]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    out: dict[str, list[dict]] = {}
    for cat, result in zip(CATEGORIES.keys(), results):
        if isinstance(result, Exception):
            logger.warning("category '%s' failed: %s", cat, result)
            out[cat] = []
        else:
            out[cat] = result
    return out


async def nearby_apartments(lat: float, lon: float, radius_m: int) -> list[dict]:
    if geoapify.is_configured() and not settings.demo_mode:
        try:
            result = await geoapify.nearby_apartments(lat, lon, radius_m)
            if result is not None:
                return _normalize(result)
        except Exception as e:
            logger.warning("Geoapify nearby_apartments failed: %s — falling back", e)

    blocks = []
    for k, v in _APARTMENT_TAGS:
        for t in ("node", "way", "relation"):
            blocks.append(f'{t}["{k}"="{v}"](around:{radius_m},{lat},{lon});')
    query = f'[out:json];({"".join(blocks)});out center;'
    key = f"overpass:apt:{lat:.4f}:{lon:.4f}:{radius_m}"
    return _normalize(await _fetch(query, key))


def nearest(
    origin_lat: float, origin_lon: float, elements: list[dict]
) -> Optional[dict]:
    if not elements:
        return None
    best = min(
        elements,
        key=lambda e: (e["lat"] - origin_lat) ** 2 + (e["lon"] - origin_lon) ** 2,
    )
    dist = geodesic((origin_lat, origin_lon), (best["lat"], best["lon"])).kilometers
    return {**best, "distance_km": dist}

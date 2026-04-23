"""Offline demo fixtures — used when DEMO_MODE=true or all Overpass mirrors fail."""
from __future__ import annotations

_APARTMENTS = [
    {"id": 101, "lat": 18.5213, "lon": 73.8545, "tags": {"name": "Sunset Heights"}},
    {"id": 102, "lat": 18.5247, "lon": 73.8601, "tags": {"name": "Green Valley Residency"}},
    {"id": 103, "lat": 18.5172, "lon": 73.8498, "tags": {"name": "Riverside Towers"}},
    {"id": 104, "lat": 18.5290, "lon": 73.8570, "tags": {"name": "Park View Apartments"}},
    {"id": 105, "lat": 18.5158, "lon": 73.8610, "tags": {"name": "Lake Vista Residency"}},
    {"id": 106, "lat": 18.5320, "lon": 73.8520, "tags": {"name": "Metro Palms"}},
    {"id": 107, "lat": 18.5110, "lon": 73.8555, "tags": {"name": "Orchid Gardens"}},
    {"id": 108, "lat": 18.5265, "lon": 73.8465, "tags": {"name": "Skyline Residences"}},
]

_CATEGORY_FIXTURES: dict[str, list[dict]] = {
    "bus_stop": [
        {"id": 201, "lat": 18.5210, "lon": 73.8560, "tags": {"name": "FC Road Stop"}},
        {"id": 202, "lat": 18.5255, "lon": 73.8590, "tags": {"name": "Shivajinagar Stop"}},
    ],
    "train_station": [
        {"id": 211, "lat": 18.5289, "lon": 73.8740, "tags": {"name": "Pune Junction"}},
    ],
    "restaurant": [
        {"id": 221, "lat": 18.5225, "lon": 73.8535, "tags": {"name": "Vaishali"}},
        {"id": 222, "lat": 18.5268, "lon": 73.8580, "tags": {"name": "Wadeshwar"}},
        {"id": 223, "lat": 18.5195, "lon": 73.8620, "tags": {"name": "Malaka Spice"}},
    ],
    "cafe": [
        {"id": 231, "lat": 18.5220, "lon": 73.8555, "tags": {"name": "Cafe Coffee Day"}},
        {"id": 232, "lat": 18.5270, "lon": 73.8595, "tags": {"name": "Starbucks FC Road"}},
    ],
    "supermarket": [
        {"id": 241, "lat": 18.5235, "lon": 73.8515, "tags": {"name": "DMart"}},
        {"id": 242, "lat": 18.5280, "lon": 73.8610, "tags": {"name": "More Megastore"}},
    ],
    "park": [
        {"id": 251, "lat": 18.5200, "lon": 73.8480, "tags": {"name": "Sambhaji Park"}},
    ],
    "hospital": [
        {"id": 261, "lat": 18.5248, "lon": 73.8553, "tags": {"name": "Ruby Hall Clinic"}},
        {"id": 262, "lat": 18.5175, "lon": 73.8645, "tags": {"name": "Jehangir Hospital"}},
    ],
    "pharmacy": [
        {"id": 271, "lat": 18.5230, "lon": 73.8550, "tags": {"name": "Apollo Pharmacy"}},
        {"id": 272, "lat": 18.5260, "lon": 73.8580, "tags": {"name": "MedPlus"}},
    ],
    "police_station": [
        {"id": 281, "lat": 18.5190, "lon": 73.8490, "tags": {"name": "Shivajinagar Police Stn"}},
    ],
    "fire_station": [
        {"id": 291, "lat": 18.5350, "lon": 73.8680, "tags": {"name": "Pune Fire Brigade"}},
    ],
    "school": [
        {"id": 301, "lat": 18.5245, "lon": 73.8530, "tags": {"name": "St. Mary's School"}},
        {"id": 302, "lat": 18.5180, "lon": 73.8580, "tags": {"name": "Loyola High School"}},
    ],
    "university": [
        {"id": 311, "lat": 18.5529, "lon": 73.8265, "tags": {"name": "Savitribai Phule Pune University"}},
    ],
    "library": [
        {"id": 321, "lat": 18.5215, "lon": 73.8505, "tags": {"name": "British Library"}},
    ],
    "shopping_mall": [
        {"id": 331, "lat": 18.5604, "lon": 73.9140, "tags": {"name": "Phoenix Marketcity"}},
        {"id": 332, "lat": 18.5155, "lon": 73.8553, "tags": {"name": "Pune Central"}},
    ],
    "movie_theater": [
        {"id": 341, "lat": 18.5225, "lon": 73.8545, "tags": {"name": "INOX Bund Garden"}},
    ],
    "museum": [
        {"id": 351, "lat": 18.5111, "lon": 73.8426, "tags": {"name": "Raja Dinkar Kelkar Museum"}},
    ],
}

_CATEGORY_MATCHERS = [
    ("cafe", '"amenity"="cafe"'),
    ("restaurant", '"amenity"="restaurant"'),
    ("hospital", '"amenity"="hospital"'),
    ("pharmacy", '"amenity"="pharmacy"'),
    ("police_station", '"amenity"="police"'),
    ("fire_station", '"amenity"="fire_station"'),
    ("school", '"amenity"="school"'),
    ("university", '"amenity"="university"'),
    ("library", '"amenity"="library"'),
    ("movie_theater", '"amenity"="cinema"'),
    ("bus_stop", '"highway"="bus_stop"'),
    ("train_station", '"railway"="station"'),
    ("supermarket", '"shop"="supermarket"'),
    ("shopping_mall", '"shop"="mall"'),
    ("park", '"leisure"="park"'),
    ("museum", '"tourism"="museum"'),
]


def fixture_for_query(query: str) -> list[dict]:
    if '"building"="apartments"' in query or '"tourism"="hotel"' in query:
        return [dict(a) for a in _APARTMENTS]
    for category, marker in _CATEGORY_MATCHERS:
        if marker in query:
            return [dict(e) for e in _CATEGORY_FIXTURES.get(category, [])]
    return []

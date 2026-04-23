from geopy.distance import geodesic


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    return geodesic(a, b).kilometers


def weighted_score(distances_km: dict[str, float], weights: dict[str, int]) -> float:
    total = sum(distances_km.get(cat, float("inf")) * w for cat, w in weights.items())
    if total == float("inf"):
        return 0.0
    return 1.0 / (1.0 + total)

from app.services.overpass import _normalize, nearest


def test_normalize_node_with_lat_lon():
    els = [{"id": 1, "lat": 12.0, "lon": 77.0, "tags": {"name": "Acme"}}]
    out = _normalize(els)
    assert out == [{"id": 1, "lat": 12.0, "lon": 77.0, "name": "Acme"}]


def test_normalize_way_with_center():
    els = [{"id": 2, "center": {"lat": 12.5, "lon": 77.5}, "tags": {}}]
    out = _normalize(els)
    assert out[0]["lat"] == 12.5
    assert out[0]["lon"] == 77.5
    assert "Unnamed" in out[0]["name"]


def test_normalize_skips_elements_without_coords():
    els = [{"id": 3, "tags": {"name": "ghost"}}]
    assert _normalize(els) == []


def test_nearest_returns_none_for_empty():
    assert nearest(0.0, 0.0, []) is None


def test_nearest_picks_closest():
    els = [
        {"lat": 10.0, "lon": 10.0, "name": "far", "id": 1},
        {"lat": 0.01, "lon": 0.01, "name": "near", "id": 2},
    ]
    result = nearest(0.0, 0.0, els)
    assert result is not None
    assert result["name"] == "near"
    assert "distance_km" in result

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_amenities_rejects_unknown_type():
    resp = client.post(
        "/api/amenities/nearby",
        json={"location": "Pune", "amenity_type": "spaceport", "radius_m": 1000},
    )
    assert resp.status_code == 400
    assert "Unknown amenity type" in resp.json()["detail"]


def test_amenities_returns_404_when_geocoding_fails():
    with patch("app.routers.amenities.geocoding.geocode", return_value=None):
        resp = client.post(
            "/api/amenities/nearby",
            json={"location": "Atlantis", "amenity_type": "hospital", "radius_m": 1000},
        )
    assert resp.status_code == 404


def test_amenities_returns_sorted_list():
    fake_elements = [
        {"name": "FarHospital", "lat": 12.1, "lon": 77.1, "id": 1},
        {"name": "NearHospital", "lat": 12.001, "lon": 77.001, "id": 2},
    ]
    with (
        patch("app.routers.amenities.geocoding.geocode", return_value=(12.0, 77.0)),
        patch(
            "app.routers.amenities.overpass.query_category",
            new=AsyncMock(return_value=fake_elements),
        ),
    ):
        resp = client.post(
            "/api/amenities/nearby",
            json={"location": "Pune", "amenity_type": "hospital", "radius_m": 1000},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["origin"] == {"lat": 12.0, "lon": 77.0}
    assert [a["name"] for a in body["amenities"]] == ["NearHospital", "FarHospital"]


def test_apartments_rejects_query_with_no_location():
    with patch("app.routers.apartments.nlp.extract_location", return_value=[]):
        resp = client.post(
            "/api/apartments/search",
            json={"query": "hello world", "radius_m": 1000},
        )
    assert resp.status_code == 400


def test_optimality_returns_verdict():
    fake_cat_data = {cat: [] for cat in __import__("app.services.overpass", fromlist=["CATEGORIES"]).CATEGORIES}
    with (
        patch("app.routers.optimality.geocoding.geocode", return_value=(22.57, 88.36)),
        patch(
            "app.routers.optimality.overpass.query_all_categories",
            new=AsyncMock(return_value=fake_cat_data),
        ),
    ):
        resp = client.post("/api/optimality/predict", json={"location": "Calcutta University"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["verdict"] in ("Optimal", "Not Optimal")
    assert body["origin"] == {"lat": 22.57, "lon": 88.36}
    assert 0.0 <= body["confidence"] <= 1.0

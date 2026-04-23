from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_openapi_docs_available() -> None:
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_apartments_validates_query_length() -> None:
    resp = client.post("/api/apartments/search", json={"query": "x", "radius_m": 1000})
    assert resp.status_code == 422

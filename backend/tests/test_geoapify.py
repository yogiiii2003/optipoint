from unittest.mock import AsyncMock, patch

import pytest

from app.services import geoapify


def test_to_elements_handles_valid_feature():
    features = [
        {
            "geometry": {"coordinates": [73.86, 18.52]},
            "properties": {"place_id": "abc", "name": "Ruby Hall"},
        }
    ]
    out = geoapify._to_elements(features)
    assert out == [
        {"id": "abc", "lat": 18.52, "lon": 73.86, "tags": {"name": "Ruby Hall"}}
    ]


def test_to_elements_skips_features_without_coords():
    features = [
        {"geometry": {}, "properties": {"name": "Ghost"}},
        {"geometry": {"coordinates": [1.0, 2.0]}, "properties": {"name": "Real"}},
    ]
    out = geoapify._to_elements(features)
    assert len(out) == 1
    assert out[0]["tags"]["name"] == "Real"


def test_to_elements_falls_back_to_address_when_no_name():
    features = [
        {
            "geometry": {"coordinates": [73.86, 18.52]},
            "properties": {"place_id": "xyz", "address_line1": "12 FC Road"},
        }
    ]
    out = geoapify._to_elements(features)
    assert out[0]["tags"]["name"] == "12 FC Road"


@pytest.mark.asyncio
async def test_query_category_returns_none_when_not_configured():
    with patch("app.services.geoapify.settings.geoapify_api_key", ""):
        result = await geoapify.query_category("hospital", 18.52, 73.85, 3000)
    assert result is None


@pytest.mark.asyncio
async def test_query_category_returns_none_for_unmapped_category():
    with patch("app.services.geoapify.settings.geoapify_api_key", "k"):
        result = await geoapify.query_category("nonexistent", 18.52, 73.85, 3000)
    assert result is None


@pytest.mark.asyncio
async def test_query_category_calls_api_and_normalizes():
    fake_resp = {
        "features": [
            {
                "geometry": {"coordinates": [73.86, 18.52]},
                "properties": {"place_id": "1", "name": "KEM"},
            }
        ]
    }

    class FakeResponse:
        def __init__(self, data):
            self._data = data

        def raise_for_status(self):
            pass

        def json(self):
            return self._data

    async def fake_get(self, url, params=None):
        assert "circle:73.85,18.52" in params["filter"]
        assert params["categories"] == "healthcare.hospital"
        return FakeResponse(fake_resp)

    with patch("app.services.geoapify.settings.geoapify_api_key", "testkey"):
        with patch("httpx.AsyncClient.get", fake_get):
            result = await geoapify.query_category("hospital", 18.52, 73.85, 3000)
    assert result == [
        {"id": "1", "lat": 18.52, "lon": 73.86, "tags": {"name": "KEM"}}
    ]


_ = AsyncMock

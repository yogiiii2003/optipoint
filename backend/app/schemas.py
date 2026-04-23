from typing import Optional

from pydantic import BaseModel, Field


class LatLon(BaseModel):
    lat: float
    lon: float


class ApartmentSearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    radius_m: int = Field(1100, ge=100, le=20000)


class NearestAmenity(BaseModel):
    name: str
    distance_km: float


class ApartmentResult(BaseModel):
    name: str
    lat: float
    lon: float
    distance_km: float
    score: float
    nearest_amenities: dict[str, NearestAmenity]


class ApartmentSearchResponse(BaseModel):
    origin: LatLon
    apartments: list[ApartmentResult]


class AmenitySearchRequest(BaseModel):
    location: str = Field(..., min_length=2)
    amenity_type: str
    radius_m: int = Field(5000, ge=100, le=50000)


class Amenity(BaseModel):
    name: str
    lat: float
    lon: float
    distance_km: float


class AmenitySearchResponse(BaseModel):
    origin: LatLon
    amenities: list[Amenity]


class OptimalityRequest(BaseModel):
    location: str = Field(..., min_length=2)


class OptimalityResponse(BaseModel):
    verdict: str
    confidence: Optional[float] = None
    origin: LatLon
    distances: dict[str, float]

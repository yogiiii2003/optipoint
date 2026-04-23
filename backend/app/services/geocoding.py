from typing import Optional, Tuple

from geopy.geocoders import Nominatim

from app.config import settings

_geolocator = Nominatim(user_agent=settings.nominatim_user_agent, timeout=10)


def geocode(location_name: str) -> Optional[Tuple[float, float]]:
    result = _geolocator.geocode(location_name)
    if result is None:
        return None
    return result.latitude, result.longitude

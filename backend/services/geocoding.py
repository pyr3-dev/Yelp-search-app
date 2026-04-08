import math

from geopy.geocoders import Nominatim
from sqlalchemy import func

from models import Business

_geocode_cache: dict[str, tuple[float, float]] = {}
_geolocator = Nominatim(user_agent="yelp-search-app")


def geocode_city(city: str) -> tuple[float, float]:
    """Return (latitude, longitude) for a city name. Results are cached in-memory."""
    if city in _geocode_cache:
        return _geocode_cache[city]
    location = _geolocator.geocode(city)
    if location is None:
        raise ValueError(f"Could not geocode city: {city}")
    coords = (location.latitude, location.longitude)
    _geocode_cache[city] = coords
    return coords


def haversine_miles_expr(center_lat: float, center_lon: float):
    """SQLAlchemy expression: great-circle distance in miles from a fixed point to Business.latitude/longitude."""
    R = 3959.0
    lat1 = math.radians(center_lat)
    lon1 = math.radians(center_lon)

    lat2 = Business.latitude * math.pi / 180
    lon2 = Business.longitude * math.pi / 180

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        func.pow(func.sin(dlat / 2), 2)
        + math.cos(lat1) * func.cos(lat2) * func.pow(func.sin(dlon / 2), 2)
    )
    return 2 * R * func.asin(func.sqrt(a))

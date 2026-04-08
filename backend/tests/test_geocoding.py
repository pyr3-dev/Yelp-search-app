import pytest
from unittest.mock import patch, MagicMock


def _clear_cache():
    from services import geocoding
    geocoding._geocode_cache.clear()


def test_geocode_city_returns_lat_lon():
    _clear_cache()
    mock_location = MagicMock()
    mock_location.latitude = 33.448
    mock_location.longitude = -112.074

    with patch("services.geocoding._geolocator") as mock_geo:
        mock_geo.geocode.return_value = mock_location
        from services.geocoding import geocode_city
        lat, lon = geocode_city("Phoenix")

    assert lat == 33.448
    assert lon == -112.074


def test_geocode_city_caches_result():
    _clear_cache()
    mock_location = MagicMock()
    mock_location.latitude = 33.448
    mock_location.longitude = -112.074

    with patch("services.geocoding._geolocator") as mock_geo:
        mock_geo.geocode.return_value = mock_location
        from services.geocoding import geocode_city
        geocode_city("Phoenix")
        geocode_city("Phoenix")

    assert mock_geo.geocode.call_count == 1


def test_geocode_city_raises_for_unknown_city():
    _clear_cache()
    with patch("services.geocoding._geolocator") as mock_geo:
        mock_geo.geocode.return_value = None
        from services.geocoding import geocode_city
        with pytest.raises(ValueError, match="Could not geocode city: Atlantis"):
            geocode_city("Atlantis")


def test_haversine_miles_expr_returns_expression():
    from sqlalchemy.sql.elements import ColumnElement
    from services.geocoding import haversine_miles_expr
    expr = haversine_miles_expr(33.448, -112.074)
    assert isinstance(expr, ColumnElement)

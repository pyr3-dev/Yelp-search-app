from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app


def _make_mock_business(**kwargs):
    b = MagicMock()
    b.business_id = kwargs.get("business_id", "abc123")
    b.name = kwargs.get("name", "Test Place")
    b.city = kwargs.get("city", "Phoenix")
    b.state = kwargs.get("state", "AZ")
    b.address = kwargs.get("address", "123 Main St")
    b.stars = kwargs.get("stars", 4.5)
    b.review_count = kwargs.get("review_count", 100)
    b.categories = kwargs.get("categories", ["Restaurants"])
    b.latitude = kwargs.get("latitude", 33.44)
    b.longitude = kwargs.get("longitude", -112.07)
    b.is_open = kwargs.get("is_open", True)
    return b


def test_search_businesses_returns_tuple():
    from services.businesses import search_businesses

    mock_db = MagicMock()
    mock_q = MagicMock()
    mock_db.query.return_value = mock_q
    mock_q.filter.return_value = mock_q
    mock_q.count.return_value = 1
    mock_q.order_by.return_value = mock_q
    mock_q.offset.return_value = mock_q
    mock_q.limit.return_value = mock_q
    mock_q.all.return_value = [_make_mock_business()]

    results, total = search_businesses(mock_db, city="Phoenix")

    assert total == 1
    assert len(results) == 1


def test_search_businesses_applies_category_filter():
    from services.businesses import search_businesses

    mock_db = MagicMock()
    mock_q = MagicMock()
    mock_db.query.return_value = mock_q
    mock_q.filter.return_value = mock_q
    mock_q.count.return_value = 0
    mock_q.order_by.return_value = mock_q
    mock_q.offset.return_value = mock_q
    mock_q.limit.return_value = mock_q
    mock_q.all.return_value = []

    results, total = search_businesses(mock_db, city="Phoenix", category="Mexican")

    # filter should have been called more than once (city + category)
    assert mock_q.filter.call_count >= 2


def test_search_businesses_respects_pagination():
    from services.businesses import search_businesses

    mock_db = MagicMock()
    mock_q = MagicMock()
    mock_db.query.return_value = mock_q
    mock_q.filter.return_value = mock_q
    mock_q.count.return_value = 50
    mock_q.order_by.return_value = mock_q
    mock_q.offset.return_value = mock_q
    mock_q.limit.return_value = mock_q
    mock_q.all.return_value = []

    search_businesses(mock_db, city="Phoenix", page=3, limit=10)

    mock_q.offset.assert_called_once_with(20)   # (page-1) * limit = 2 * 10
    mock_q.limit.assert_called_once_with(10)


# --- API-level tests ---

client = TestClient(app)


def _mock_business_dict():
    return {
        "business_id": "test_biz_001",
        "name": "Joe's Diner",
        "address": "100 Main St",
        "city": "Phoenix",
        "state": "AZ",
        "stars": 4.5,
        "review_count": 250,
        "categories": ["Diners", "American"],
        "latitude": 33.44,
        "longitude": -112.07,
        "is_open": True,
    }


def test_get_businesses_requires_city():
    response = client.get("/businesses")
    assert response.status_code == 422   # city is required


def test_get_businesses_returns_200():
    d = _mock_business_dict()
    mock_biz = MagicMock()
    for k, v in d.items():
        setattr(mock_biz, k, v)
    with patch("controllers.businesses.search_businesses") as mock_svc:
        mock_svc.return_value = ([mock_biz], 1)
        response = client.get("/businesses?city=Phoenix")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["page"] == 1
    assert data["results"][0]["name"] == "Joe's Diner"


def test_get_businesses_pagination_params():
    with patch("controllers.businesses.search_businesses") as mock_svc:
        mock_svc.return_value = ([], 0)
        response = client.get("/businesses?city=Phoenix&page=2&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["limit"] == 5
    mock_svc.assert_called_once()
    call_kwargs = mock_svc.call_args.kwargs
    assert call_kwargs["page"] == 2
    assert call_kwargs["limit"] == 5


def test_get_business_detail_not_found():
    with patch("controllers.businesses.get_business_detail") as mock_svc:
        mock_svc.return_value = None
        response = client.get("/businesses/nonexistent_id")
    assert response.status_code == 404


def test_get_business_reviews_returns_200():
    with patch("controllers.businesses.get_business_reviews") as mock_svc:
        mock_svc.return_value = ([], 0)
        response = client.get("/businesses/test_biz_001/reviews")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["results"] == []


def test_get_business_photos_returns_200():
    with patch("controllers.businesses.get_business_photos") as mock_svc:
        mock_svc.return_value = []
        response = client.get("/businesses/test_biz_001/photos")
    assert response.status_code == 200
    assert response.json() == []


def test_get_business_detail_happy_path():
    from datetime import datetime

    mock_biz = MagicMock()
    mock_biz.__table__ = MagicMock()
    # Set up columns to iterate: simulate business.__table__.columns
    col_business_id = MagicMock(); col_business_id.name = "business_id"
    col_name = MagicMock(); col_name.name = "name"
    col_city = MagicMock(); col_city.name = "city"
    col_stars = MagicMock(); col_stars.name = "stars"
    col_review_count = MagicMock(); col_review_count.name = "review_count"
    col_address = MagicMock(); col_address.name = "address"
    col_state = MagicMock(); col_state.name = "state"
    col_postal_code = MagicMock(); col_postal_code.name = "postal_code"
    col_latitude = MagicMock(); col_latitude.name = "latitude"
    col_longitude = MagicMock(); col_longitude.name = "longitude"
    col_is_open = MagicMock(); col_is_open.name = "is_open"
    col_attributes = MagicMock(); col_attributes.name = "attributes"
    col_categories = MagicMock(); col_categories.name = "categories"
    col_hours = MagicMock(); col_hours.name = "hours"
    mock_biz.__table__.columns = [
        col_business_id, col_name, col_city, col_stars, col_review_count,
        col_address, col_state, col_postal_code, col_latitude, col_longitude,
        col_is_open, col_attributes, col_categories, col_hours,
    ]
    mock_biz.business_id = "test_biz_001"
    mock_biz.name = "Joe's Diner"
    mock_biz.city = "Phoenix"
    mock_biz.stars = 4.5
    mock_biz.review_count = 250
    mock_biz.address = "100 Main St"
    mock_biz.state = "AZ"
    mock_biz.postal_code = "85001"
    mock_biz.latitude = 33.44
    mock_biz.longitude = -112.07
    mock_biz.is_open = True
    mock_biz.attributes = {}
    mock_biz.categories = ["Diners"]
    mock_biz.hours = {}

    mock_tip = MagicMock()
    mock_tip.id = 1
    mock_tip.text = "Great place"
    mock_tip.date = datetime(2023, 6, 15, 12, 0, 0)
    mock_tip.compliment_count = 3
    mock_tip.user_id = "user_xyz"

    with patch("controllers.businesses.get_business_detail") as mock_svc:
        mock_svc.return_value = (mock_biz, [mock_tip], 5)
        response = client.get("/businesses/test_biz_001")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Joe's Diner"
    assert data["checkin_count"] == 5
    assert len(data["tips"]) == 1
    assert data["tips"][0]["text"] == "Great place"


def test_get_business_reviews_with_datetime():
    from datetime import datetime

    mock_review = MagicMock()
    mock_review.review_id = "rev_001"
    mock_review.user_id = "user_abc"
    mock_review.stars = 4
    mock_review.date = datetime(2023, 3, 10, 8, 0, 0)
    mock_review.text = "Great food"
    mock_review.useful = 1
    mock_review.funny = 0
    mock_review.cool = 2

    with patch("controllers.businesses.get_business_reviews") as mock_svc:
        mock_svc.return_value = ([mock_review], 1)
        response = client.get("/businesses/test_biz_001/reviews")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["results"][0]["review_id"] == "rev_001"
    assert data["results"][0]["stars"] == 4
    assert "2023" in data["results"][0]["date"]

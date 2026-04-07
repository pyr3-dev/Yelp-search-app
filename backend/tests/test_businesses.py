from unittest.mock import MagicMock


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

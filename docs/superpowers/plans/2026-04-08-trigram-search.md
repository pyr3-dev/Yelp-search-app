# Trigram Search + Optional Geo Radius Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add fuzzy city/name matching via pg_trgm and an optional `scope=radius` mode that geocodes the city and filters businesses within 5 miles using a SQL Haversine expression.

**Architecture:** A new Alembic migration enables `pg_trgm` and adds GIN indexes. `services/geocoding.py` owns Nominatim geocoding (with an in-memory cache) and the Haversine SQL expression. `services/businesses.py` replaces `ilike` with `func.similarity` and branches on `scope`. The controller catches `ValueError` from geocoding and re-raises as HTTP 422.

**Tech Stack:** PostgreSQL `pg_trgm`, SQLAlchemy `func.similarity` / `func.sin` / `func.cos` / `func.asin` / `func.sqrt`, geopy `Nominatim`, FastAPI, pytest + `unittest.mock`

---

## File Map

| Action | Path | Responsibility |
|---|---|---|
| Create | `backend/alembic/versions/XXXX_add_pg_trgm_indexes.py` | Enable `pg_trgm`, GIN indexes on `business.city` and `business.name` |
| Create | `backend/services/geocoding.py` | `geocode_city()` with in-memory cache, `haversine_miles_expr()` SQL expression |
| Create | `backend/tests/test_geocoding.py` | Unit tests for geocoding service (Nominatim mocked) |
| Modify | `backend/services/businesses.py` | Trigram filters, `name`/`scope` params, relevance ranking |
| Modify | `backend/controllers/businesses.py` | Add `name`, `scope` params; catch `ValueError` → HTTP 422 |
| Modify | `backend/routes/businesses.py` | Add `name`, `scope` params; update `sort_by` literal |
| Modify | `backend/tests/test_businesses.py` | Tests for new params and scope=radius geocode failure |
| Modify | `backend/pyproject.toml` | Add `geopy>=2.4.0` |

---

## Task 1: Add geopy dependency

**Files:**
- Modify: `backend/pyproject.toml`

- [ ] **Step 1: Add geopy to dependencies**

In `backend/pyproject.toml`, add `"geopy>=2.4.0"` to the `dependencies` list:

```toml
dependencies = [
    "alembic>=1.18.4",
    "geopy>=2.4.0",
    "pandas>=2.0.0",
    "bcrypt>=5.0.0",
    "fastapi[standard]>=0.135.3",
    "httpx>=0.27.0",
    "pgvector>=0.3.6",
    "psycopg2>=2.9.11",
    "pyjwt>=2.12.1",
    "python-dotenv>=1.2.2",
    "python-multipart>=0.0.22",
    "sentence-transformers>=3.4.0",
]
```

- [ ] **Step 2: Install**

Run from `backend/`:
```bash
uv pip install -e ".[dev]"
```

Expected: installs geopy without errors.

- [ ] **Step 3: Verify import**

```bash
python -c "from geopy.geocoders import Nominatim; print('ok')"
```

Expected: `ok`

- [ ] **Step 4: Commit**

```bash
git add backend/pyproject.toml backend/uv.lock
git commit -m "chore: add geopy dependency"
```

---

## Task 2: Alembic migration — pg_trgm extension + GIN indexes

**Files:**
- Create: `backend/alembic/versions/XXXX_add_pg_trgm_indexes.py`

- [ ] **Step 1: Generate migration shell**

Run from `backend/`:
```bash
alembic revision -m "add_pg_trgm_indexes"
```

This creates a new file in `alembic/versions/`. Open it — note the generated `revision` hash and that `down_revision` should be `"954a910e0046"` (the pgvector migration). If it isn't, fix it manually.

- [ ] **Step 2: Fill in the migration**

Replace the generated `upgrade` and `downgrade` functions with:

```python
def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute(
        "CREATE INDEX business_city_trgm_idx ON business USING gin (city gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX business_name_trgm_idx ON business USING gin (name gin_trgm_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS business_name_trgm_idx")
    op.execute("DROP INDEX IF EXISTS business_city_trgm_idx")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
```

- [ ] **Step 3: Run the migration**

```bash
alembic upgrade head
```

Expected: migration runs without errors.

- [ ] **Step 4: Verify in psql**

```bash
docker exec -it <postgres-container> psql -U postgres -d postgres -c "\dx pg_trgm"
```

Expected: one row showing `pg_trgm` extension.

- [ ] **Step 5: Commit**

```bash
git add backend/alembic/versions/
git commit -m "feat: enable pg_trgm extension and add trigram indexes on business city and name"
```

---

## Task 3: Create geocoding service (TDD)

**Files:**
- Create: `backend/services/geocoding.py`
- Create: `backend/tests/test_geocoding.py`

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/test_geocoding.py`:

```python
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
    from services.geocoding import haversine_miles_expr
    expr = haversine_miles_expr(33.448, -112.074)
    assert expr is not None
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_geocoding.py -v
```

Expected: `ModuleNotFoundError: No module named 'services.geocoding'`

- [ ] **Step 3: Implement geocoding service**

Create `backend/services/geocoding.py`:

```python
import math

from geopy.geocoders import Nominatim
from sqlalchemy import func, cast, Float

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

    lat2 = cast(Business.latitude, Float) * math.pi / 180
    lon2 = cast(Business.longitude, Float) * math.pi / 180

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        func.pow(func.sin(dlat / 2), 2)
        + math.cos(lat1) * func.cos(lat2) * func.pow(func.sin(dlon / 2), 2)
    )
    return 2 * R * func.asin(func.sqrt(a))
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest tests/test_geocoding.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/services/geocoding.py backend/tests/test_geocoding.py
git commit -m "feat: add geocoding service with Nominatim and Haversine SQL expression"
```

---

## Task 4: Update search service with trigram + name + scope (TDD)

**Files:**
- Modify: `backend/services/businesses.py`
- Modify: `backend/tests/test_businesses.py`

- [ ] **Step 1: Write failing tests for new behavior**

Add these tests to the bottom of `backend/tests/test_businesses.py`:

```python
def test_search_businesses_accepts_name_param():
    from services.businesses import search_businesses

    mock_db = MagicMock()
    mock_q = MagicMock()
    mock_db.query.return_value = mock_q
    mock_q.filter.return_value = mock_q
    mock_q.count.return_value = 0
    mock_q.order_by.return_value = mock_q
    mock_q.add_columns.return_value = mock_q
    mock_q.offset.return_value = mock_q
    mock_q.limit.return_value = mock_q
    mock_q.all.return_value = []

    results, total = search_businesses(mock_db, city="Phoenix", name="Dominos")
    assert total == 0
    # name filter triggers an additional filter call (city + name = at least 2)
    assert mock_q.filter.call_count >= 2


def test_search_businesses_accepts_scope_param():
    from services.businesses import search_businesses
    from unittest.mock import patch

    mock_db = MagicMock()
    mock_q = MagicMock()
    mock_db.query.return_value = mock_q
    mock_q.filter.return_value = mock_q
    mock_q.count.return_value = 0
    mock_q.order_by.return_value = mock_q
    mock_q.add_columns.return_value = mock_q
    mock_q.offset.return_value = mock_q
    mock_q.limit.return_value = mock_q
    mock_q.all.return_value = []
    mock_q.scalar.return_value = "Phoenix"

    with patch("services.geocoding.geocode_city", return_value=(33.448, -112.074)):
        results, total = search_businesses(mock_db, city="Phoenix", scope="radius")
    assert total == 0


def test_search_businesses_radius_no_city_match_returns_empty():
    from services.businesses import search_businesses

    mock_db = MagicMock()
    mock_q = MagicMock()
    mock_db.query.return_value = mock_q
    mock_q.filter.return_value = mock_q
    mock_q.scalar.return_value = None  # no city found via trigram

    results, total = search_businesses(mock_db, city="zzzzz", scope="radius")
    assert results == []
    assert total == 0
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_businesses.py::test_search_businesses_accepts_name_param \
       tests/test_businesses.py::test_search_businesses_accepts_scope_param \
       tests/test_businesses.py::test_search_businesses_radius_no_city_match_returns_empty -v
```

Expected: failures — `search_businesses` doesn't accept `name` or `scope` yet.

- [ ] **Step 3: Rewrite `services/businesses.py`**

Replace the entire file with:

```python
import math
from typing import Literal, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models import Business, Checkin, Photo, Review, Tip

SIMILARITY_THRESHOLD = 0.3


def search_businesses(
    db: Session,
    city: str,
    category: Optional[str] = None,
    min_stars: Optional[float] = None,
    name: Optional[str] = None,
    scope: Literal["city", "radius"] = "city",
    sort_by: Literal["relevance", "stars", "review_count", "name"] = "relevance",
    order: Literal["asc", "desc"] = "desc",
    page: int = 1,
    limit: int = 20,
) -> tuple[list[tuple[Business, str | None]], int]:
    if scope == "radius":
        from services.geocoding import geocode_city, haversine_miles_expr
        canonical = (
            db.query(Business.city)
            .filter(func.similarity(Business.city, city) > SIMILARITY_THRESHOLD)
            .order_by(func.similarity(Business.city, city).desc())
            .limit(1)
            .scalar()
        )
        if canonical is None:
            return [], 0
        center_lat, center_lon = geocode_city(canonical)
        distance_expr = haversine_miles_expr(center_lat, center_lon)
        query = db.query(Business).filter(distance_expr <= 5.0)
    else:
        query = db.query(Business).filter(
            func.similarity(Business.city, city) > SIMILARITY_THRESHOLD
        )

    if name:
        query = query.filter(
            func.similarity(Business.name, name) > SIMILARITY_THRESHOLD
        )
    if category:
        query = query.filter(Business.categories.contains([category]))
    if min_stars is not None:
        query = query.filter(Business.stars >= min_stars)

    total = query.count()

    if sort_by == "relevance":
        city_sim = func.similarity(Business.city, city)
        relevance = (
            (city_sim + func.similarity(Business.name, name)) / 2
            if name
            else city_sim
        )
        sort_expr = relevance.desc() if order == "desc" else relevance.asc()
    else:
        sort_col = {
            "review_count": Business.review_count,
            "name": Business.name,
            "stars": Business.stars,
        }.get(sort_by, Business.stars)
        sort_expr = sort_col.asc() if order == "asc" else sort_col.desc()

    first_photo_subq = (
        select(Photo.photo_id)
        .where(Photo.business_id == Business.business_id)
        .limit(1)
        .correlate(Business)
        .scalar_subquery()
    )

    rows = (
        query.order_by(sort_expr)
        .add_columns(first_photo_subq.label("first_photo_id"))
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return [(row[0], row[1]) for row in rows], total


def get_business_detail(
    db: Session, business_id: str
) -> Optional[tuple[Business, list[Tip], int]]:
    business = db.query(Business).filter(
        Business.business_id == business_id
    ).first()
    if not business:
        return None

    tips = (
        db.query(Tip)
        .filter(Tip.business_id == business_id)
        .order_by(Tip.date.desc())
        .limit(5)
        .all()
    )
    checkin = db.query(Checkin).filter(
        Checkin.business_id == business_id
    ).first()
    checkin_count = (
        len(checkin.dates.split(",")) if checkin and checkin.dates else 0
    )
    return business, tips, checkin_count


def get_business_reviews(
    db: Session,
    business_id: str,
    page: int = 1,
    limit: int = 20,
    sort_by: Literal["date", "stars"] = "date",
    order: Literal["asc", "desc"] = "desc",
) -> tuple[list[Review], int]:
    query = db.query(Review).filter(Review.business_id == business_id)
    total = query.count()

    sort_col = Review.stars if sort_by == "stars" else Review.date
    query = query.order_by(
        sort_col.asc() if order == "asc" else sort_col.desc()
    )
    results = query.offset((page - 1) * limit).limit(limit).all()
    return results, total


def get_business_photos(db: Session, business_id: str) -> list[Photo]:
    return db.query(Photo).filter(Photo.business_id == business_id).all()
```

- [ ] **Step 4: Run new tests — verify they pass**

```bash
pytest tests/test_businesses.py::test_search_businesses_accepts_name_param \
       tests/test_businesses.py::test_search_businesses_accepts_scope_param \
       tests/test_businesses.py::test_search_businesses_radius_no_city_match_returns_empty -v
```

Expected: 3 passed.

- [ ] **Step 5: Run full test suite — verify nothing regressed**

```bash
pytest tests/test_businesses.py -v
```

Expected: all previously passing tests still pass. The existing mock-based tests (`test_search_businesses_returns_tuple`, etc.) will need their mocks updated because `add_columns` is now called on the query chain. If any fail due to mock chain issues, add `mock_q.add_columns.return_value = mock_q` to the failing test's setup.

- [ ] **Step 6: Commit**

```bash
git add backend/services/businesses.py backend/tests/test_businesses.py
git commit -m "feat: replace ilike with pg_trgm similarity and add name/scope search params"
```

---

## Task 5: Wire new params through controller and route

**Files:**
- Modify: `backend/controllers/businesses.py`
- Modify: `backend/routes/businesses.py`
- Modify: `backend/tests/test_businesses.py`

- [ ] **Step 1: Write failing API-level tests**

Add these tests to the bottom of `backend/tests/test_businesses.py`:

```python
def test_search_passes_name_param_to_service():
    with patch("controllers.businesses.search_businesses") as mock_svc:
        mock_svc.return_value = ([], 0)
        response = client.get("/businesses?city=Phoenix&name=Dominos")
    assert response.status_code == 200
    assert mock_svc.call_args.kwargs["name"] == "Dominos"


def test_search_passes_scope_radius_to_service():
    with patch("controllers.businesses.search_businesses") as mock_svc:
        mock_svc.return_value = ([], 0)
        response = client.get("/businesses?city=Phoenix&scope=radius")
    assert response.status_code == 200
    assert mock_svc.call_args.kwargs["scope"] == "radius"


def test_search_scope_radius_geocode_failure_returns_422():
    with patch("controllers.businesses.search_businesses") as mock_svc:
        mock_svc.side_effect = ValueError("Could not geocode city: Atlantis")
        response = client.get("/businesses?city=Atlantis&scope=radius")
    assert response.status_code == 422
    assert "Could not geocode city" in response.json()["detail"]


def test_search_default_sort_by_is_relevance():
    with patch("controllers.businesses.search_businesses") as mock_svc:
        mock_svc.return_value = ([], 0)
        response = client.get("/businesses?city=Phoenix")
    assert response.status_code == 200
    assert mock_svc.call_args.kwargs["sort_by"] == "relevance"


def test_search_invalid_scope_returns_422():
    response = client.get("/businesses?city=Phoenix&scope=invalid")
    assert response.status_code == 422
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_businesses.py::test_search_passes_name_param_to_service \
       tests/test_businesses.py::test_search_passes_scope_radius_to_service \
       tests/test_businesses.py::test_search_scope_radius_geocode_failure_returns_422 \
       tests/test_businesses.py::test_search_default_sort_by_is_relevance \
       tests/test_businesses.py::test_search_invalid_scope_returns_422 -v
```

Expected: failures — route doesn't accept `name` or `scope` yet.

- [ ] **Step 3: Update `controllers/businesses.py`**

Replace `search_controller` with:

```python
async def search_controller(
    city: Annotated[str, Query(description="City name")],
    category: Annotated[Optional[str], Query()] = None,
    min_stars: Annotated[Optional[float], Query(ge=0.0, le=5.0)] = None,
    name: Annotated[Optional[str], Query()] = None,
    scope: Annotated[Literal["city", "radius"], Query()] = "city",
    sort_by: Annotated[
        Literal["relevance", "stars", "review_count", "name"], Query()
    ] = "relevance",
    order: Annotated[Literal["asc", "desc"], Query()] = "desc",
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    db: Session = Depends(get_db),
) -> BusinessSearchResponse:
    try:
        rows, total = search_businesses(
            db,
            city=city,
            category=category,
            min_stars=min_stars,
            name=name,
            scope=scope,
            sort_by=sort_by,
            order=order,
            page=page,
            limit=limit,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    results = [
        BusinessDetail(
            **{c.name: getattr(business, c.name) for c in business.__table__.columns},
            first_photo_id=first_photo_id,
        )
        for business, first_photo_id in rows
    ]
    return BusinessSearchResponse(
        total=total,
        page=page,
        limit=limit,
        results=results,
    )
```

Also add `Literal` to the imports at the top of the file if not already present:
```python
from typing import Annotated, Literal, Optional
```

- [ ] **Step 4: Update `routes/businesses.py`**

Replace the `search` route with:

```python
@router.get("", response_model=BusinessSearchResponse)
async def search(
    city: Annotated[str, Query()],
    category: Annotated[Optional[str], Query()] = None,
    min_stars: Annotated[Optional[float], Query(ge=0.0, le=5.0)] = None,
    name: Annotated[Optional[str], Query()] = None,
    scope: Annotated[Literal["city", "radius"], Query()] = "city",
    sort_by: Annotated[
        Literal["relevance", "stars", "review_count", "name"], Query()
    ] = "relevance",
    order: Annotated[Literal["asc", "desc"], Query()] = "desc",
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    db: Annotated[Session, Depends(get_db)] = None,
):
    return await search_controller(
        city=city,
        category=category,
        min_stars=min_stars,
        name=name,
        scope=scope,
        sort_by=sort_by,
        order=order,
        page=page,
        limit=limit,
        db=db,
    )
```

Also ensure `Literal` is imported at the top:
```python
from typing import Annotated, Literal, Optional
```

- [ ] **Step 5: Run new API tests — verify they pass**

```bash
pytest tests/test_businesses.py::test_search_passes_name_param_to_service \
       tests/test_businesses.py::test_search_passes_scope_radius_to_service \
       tests/test_businesses.py::test_search_scope_radius_geocode_failure_returns_422 \
       tests/test_businesses.py::test_search_default_sort_by_is_relevance \
       tests/test_businesses.py::test_search_invalid_scope_returns_422 -v
```

Expected: 5 passed.

- [ ] **Step 6: Run the full test suite**

```bash
pytest -v
```

Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add backend/controllers/businesses.py backend/routes/businesses.py backend/tests/test_businesses.py
git commit -m "feat: wire name and scope params through route and controller"
```

---

## Task 6: Manual end-to-end verification

**Files:** none — verification only

- [ ] **Step 1: Start the server**

```bash
# Terminal 1 — from repo root
docker-compose up

# Terminal 2 — from backend/
fastapi dev main.py
```

- [ ] **Step 2: Fuzzy city search (scope=city)**

```bash
curl "http://localhost:8000/businesses?city=Phoenx" | python -m json.tool | head -30
```

Expected: results with `city` values like "Phoenix", ranked by similarity score.

- [ ] **Step 3: Name search**

```bash
curl "http://localhost:8000/businesses?city=Phoenix&name=Dominos" | python -m json.tool | head -30
```

Expected: results with names similar to "Dominos" (e.g., "Domino's Pizza").

- [ ] **Step 4: Radius mode**

```bash
curl "http://localhost:8000/businesses?city=Phoenix&scope=radius" | python -m json.tool | head -30
```

Expected: results that are within 5 miles of Phoenix's geocoded centroid. May include businesses from adjacent cities (Scottsdale, Tempe, etc.) that are geographically close.

- [ ] **Step 5: Radius mode geocode failure**

```bash
curl "http://localhost:8000/businesses?city=Zzzznotacity&scope=radius"
```

Expected:
```json
{"detail": "Could not geocode city: Zzzznotacity"}
```
with HTTP 422.

- [ ] **Step 6: Sort by stars still works**

```bash
curl "http://localhost:8000/businesses?city=Phoenix&sort_by=stars&order=desc" | python -m json.tool | head -20
```

Expected: results ordered by `stars` descending.

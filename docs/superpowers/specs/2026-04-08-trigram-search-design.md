# Trigram Search + Optional Geo Radius Design

**Date:** 2026-04-08  
**Scope:** Backend only — `services/`, `routes/`, `controllers/`, `schema.py`, new Alembic migration

---

## Overview

Upgrade the business search endpoint with two improvements:

1. **Fuzzy city and name matching** via PostgreSQL `pg_trgm` — handles typos in both the `city` and new optional `name` query params
2. **Optional geo radius mode** — when `scope=radius`, geocode the resolved city to a lat/lng centroid and filter by ≤ 5 miles using a SQL Haversine expression

---

## New Query Parameters

| Param | Type | Default | Description |
|---|---|---|---|
| `name` | `string` | `null` | Optional fuzzy filter on business name |
| `scope` | `"city" \| "radius"` | `"city"` | Search scope mode |
| `sort_by` | `"relevance" \| "stars" \| "review_count" \| "name"` | `"relevance"` | `"relevance"` ranks by trigram similarity score |

`sort_by` default changes from `"stars"` to `"relevance"`. Clients that previously omitted `sort_by` will now see results ordered by match quality instead of star rating.

---

## Search Modes

### `scope=city` (default)

1. Filter `Business.city` by `similarity(city, query) > 0.3` using pg_trgm
2. If `name` provided, additionally filter `Business.name` by `similarity(name, query) > 0.3`
3. Compute relevance score: average of active similarity values
4. If `sort_by=relevance`, order by relevance desc; otherwise order by the chosen column

### `scope=radius`

1. Resolve canonical city name: `SELECT DISTINCT city ORDER BY similarity(city, input) DESC LIMIT 1` — finds the closest matching city string in the dataset
2. Geocode the canonical city via Nominatim (geopy) → `(lat, lng)` centroid. Result is cached in-memory keyed by city string.
3. Filter businesses using a SQL Haversine expression on `Business.latitude / Business.longitude` — `haversine_miles(centroid, business) <= 5.0`. No city string filter is applied in this mode.
4. If `name` provided, additionally filter `Business.name` by trigram similarity > 0.3
5. Relevance scoring and `sort_by` behave the same as `scope=city`

---

## Architecture Changes

### New migration

```
alembic revision -m "add pg_trgm extension and trigram indexes"
```

Contents:
- `CREATE EXTENSION IF NOT EXISTS pg_trgm`
- `CREATE INDEX business_city_trgm_idx ON business USING gin (city gin_trgm_ops)`
- `CREATE INDEX business_name_trgm_idx ON business USING gin (name gin_trgm_ops)`

Down migration drops the indexes and the extension.

### New file: `services/geocoding.py`

Two responsibilities:
- `geocode_city(city: str) -> tuple[float, float]` — calls Nominatim, caches result in a module-level dict, raises `ValueError` if city cannot be geocoded
- `haversine_miles_expr(lat, lon)` — returns a SQLAlchemy column expression computing great-circle distance in miles from a fixed centroid point to `Business.latitude / Business.longitude`

Nominatim `user_agent` is set to `"yelp-search-app"`. No API key required.

### `services/businesses.py`

`search_businesses` signature gains:
- `name: Optional[str] = None`
- `scope: Literal["city", "radius"] = "city"`
- `sort_by` type widens to include `"relevance"`

Internal logic branches on `scope`. Similarity threshold `SIMILARITY_THRESHOLD = 0.3` defined as a module-level constant.

### `schema.py`

- `BusinessSearchResponse` — no changes
- Route-level query param annotations updated to include `name`, `scope`, and `"relevance"` in the `sort_by` literal

### `routes/businesses.py` / `controllers/businesses.py`

Pass `name` and `scope` through the existing route → controller → service chain. No structural changes.

---

## Error Handling

- If `scope=radius` and Nominatim cannot resolve the city, return HTTP 422 with message `"Could not geocode city: {city}"`
- Nominatim network errors propagate as HTTP 502
- `scope=city` has no new error paths

---

## Similarity Threshold

`0.3` (pg_trgm default). Hardcoded constant — no runtime configuration. Can be adjusted in a single place (`SIMILARITY_THRESHOLD` in `services/businesses.py`) if tuning is needed after testing against the dataset.

---

## Geocode Cache

Module-level `dict[str, tuple[float, float]]` in `services/geocoding.py`. Populated lazily on first request per city. No TTL — city centroids don't change. Cache is process-scoped (reset on server restart). No persistence needed.

---

## Dependencies

Add to `pyproject.toml`:
- `geopy>=2.4.0`

---

## Testing

- Unit test `haversine_miles_expr` against known coordinate pairs
- Unit test `geocode_city` with Nominatim mocked
- Integration test `search_businesses` with `scope=city`: verify trigram match returns results for a misspelled city, verify no results for a completely wrong city
- Integration test `search_businesses` with `scope=radius`: verify businesses within 5 miles are returned, verify businesses beyond 5 miles are excluded
- Integration test: `name` filter returns fuzzy name matches, exact misses are excluded

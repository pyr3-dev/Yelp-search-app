# Yelp Search App — Design Spec
**Date:** 2026-04-08

## Overview

A restaurant search web app backed by the locally-downloaded Yelp Open Dataset. Users search by city with optional filters (category, min stars, sort order). The FastAPI backend ingests the dataset into PostgreSQL via Alembic migrations and exposes a REST API. A React frontend consumes the API.

Auth is optional — all search endpoints are public, but the existing JWT auth system is retained for future authenticated features.

---

## 1. Database Schema

Six new SQLAlchemy models added to `models.py`. The existing `User` model is untouched.

### Business
Primary table. Fully ingested from `business.json`.

| Column | Type | Notes |
|---|---|---|
| business_id | String(22) | PK |
| name | String | |
| address | String | |
| city | String | indexed |
| state | String(2) | |
| postal_code | String(10) | |
| latitude | Float | |
| longitude | Float | |
| stars | Float | indexed |
| review_count | Integer | indexed |
| is_open | Boolean | |
| attributes | JSONB | |
| categories | ARRAY(String) | GIN indexed |
| hours | JSONB | |

### YelpUser
Stripped-down ingestion of `user.json`. Drops friends array and all compliment fields.

| Column | Type |
|---|---|
| user_id | String(22) PK |
| name | String |
| review_count | Integer |
| yelping_since | Date |
| average_stars | Float |
| fans | Integer |

### Review
From `review.json` (~6.9M rows). No FK constraint on `user_id` — enforcing it on 6.9M rows at insert time is too slow.

| Column | Type | Notes |
|---|---|---|
| review_id | String(22) | PK |
| user_id | String(22) | no FK |
| business_id | String(22) | FK → Business, indexed |
| stars | SmallInteger | |
| date | Date | |
| text | Text | |
| useful | Integer | |
| funny | Integer | |
| cool | Integer | |

### Tip
From `tip.json`.

| Column | Type | Notes |
|---|---|---|
| id | Integer | PK (auto) |
| text | Text | |
| date | Date | |
| compliment_count | Integer | |
| business_id | String(22) | FK → Business, indexed |
| user_id | String(22) | no FK |

### Checkin
From `checkin.json`. One row per business. Timestamps stored as comma-separated string (matches source format).

| Column | Type | Notes |
|---|---|---|
| id | Integer | PK (auto) |
| business_id | String(22) | FK → Business, unique |
| dates | Text | comma-separated timestamps |

### Photo
From `photo.json`. Metadata only — actual image files not served by this app.

| Column | Type | Notes |
|---|---|---|
| photo_id | String(22) | PK |
| business_id | String(22) | FK → Business, indexed |
| caption | Text | |
| label | String(10) | food/drink/menu/inside/outside |

---

## 2. Migrations & Ingestion

### Migration 1 — DDL: `create_yelp_tables`
Creates all 6 tables and their indexes. No data. Safe to run on a clean or existing DB.

### Migration 2 — Data: `ingest_yelp_dataset`
Reads `YELP_DATASET_PATH` from environment. Streams each file line-by-line (newline-delimited JSON). Inserts in batches of 1000 using `INSERT ... ON CONFLICT DO NOTHING` — idempotent, safe to re-run.

**Ingestion order** (FK-safe):
1. `user.json` → YelpUser
2. `business.json` → Business
3. `review.json` → Review (logs progress every 100k rows)
4. `tip.json` → Tip
5. `checkin.json` → Checkin
6. `photo.json` → Photo

Uses raw `connection.execute()` (not ORM) for bulk insert performance. Files are never fully loaded into memory.

Raises a clear error at migration start if `YELP_DATASET_PATH` is missing or any expected file is not found.

**New env variable** (added to `.env.example`):
```
YELP_DATASET_PATH=/path/to/yelp_dataset
```

---

## 3. Backend API

Follows existing `routes → controllers → services` layering. All endpoints are public (no auth required).

**New files:**
- `routes/businesses.py`
- `controllers/businesses.py`
- `services/businesses.py`

Pydantic schemas for all requests/responses added to `schema.py`.

### Endpoints

#### `GET /businesses`
Search businesses by city with optional filters.

**Query params:**

| Param | Type | Default | Notes |
|---|---|---|---|
| city | string | required | case-insensitive match |
| category | string | — | matches any item in categories array |
| min_stars | float | — | 0.0–5.0 |
| sort_by | enum | stars | stars \| review_count \| name |
| order | enum | desc | asc \| desc |
| page | int | 1 | |
| limit | int | 20 | max 100 |

**Response:**
```json
{
  "total": 1234,
  "page": 1,
  "limit": 20,
  "results": [
    {
      "business_id": "...",
      "name": "...",
      "address": "...",
      "city": "...",
      "state": "...",
      "stars": 4.5,
      "review_count": 1198,
      "categories": ["Mexican", "Burgers"],
      "latitude": 37.78,
      "longitude": -122.39,
      "is_open": true
    }
  ]
}
```

#### `GET /businesses/{business_id}`
Full business detail including recent tips (last 5) and checkin count.

#### `GET /businesses/{business_id}/reviews`
Paginated reviews for a business.

**Query params:** `page`, `limit`, `sort_by` (date | stars), `order`

#### `GET /businesses/{business_id}/photos`
Photo metadata list for a business.

**Response:** list of `{ photo_id, caption, label }`

---

## 4. React Frontend (phase 2 — after backend is complete)

Vite + React in `frontend/` at repo root. Uses React Query for data fetching.

**Views:**
1. **Search page** — city input + category dropdown, min-stars slider, sort controls
2. **Results list** — cards with name, stars, address, coordinates, category tags, open/closed badge, pagination
3. **Business detail** — full info + reviews tab + photos tab

Auth pages (login/register) wired to existing endpoints but not required to use search.

---

## 5. What's Kept vs. Changed

| Component | Status |
|---|---|
| `User` model | Unchanged |
| Auth routes/controllers/services | Unchanged |
| `main.py` CORS setup | Add search router include |
| `models.py` | Add 6 new models |
| `schema.py` | Add business search schemas |
| `dependencies.py` | Unchanged |
| `.env.example` | Add `YELP_DATASET_PATH` |
| Alembic | 2 new migrations |

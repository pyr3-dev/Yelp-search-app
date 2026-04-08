# Yelp Search App

Restaurant search app backed by the locally-downloaded Yelp Open Dataset. Users search by city with optional filters (category, stars, name, sort, scope). FastAPI backend + PostgreSQL + React frontend.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package manager)
- [Node.js](https://nodejs.org/) (for the frontend)
- [Yelp Open Dataset](https://www.yelp.com/dataset) downloaded and extracted locally

---

## Setup

### 1. Start PostgreSQL

```bash
docker-compose up -d
```

This starts a `pgvector/pgvector:pg16` container on port 5432 with persistent volume `pgdata`.

### 2. Install Python dependencies

```bash
cd backend
uv sync
```

### 3. Configure environment

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` with your values:

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string — default works with the Docker setup |
| `JWT_SECRET` | Any random string |
| `REFRESH_SECRET` | Any random string |
| `FRONTEND_URL` | `http://localhost:5173` for local dev |
| `YELP_DATASET_PATH` | Absolute path to the folder containing the main Yelp JSON files |
| `YELP_PHOTO_DATASET_PATH` | Absolute path to the folder containing `photos.json` |

### 4. Run database migrations

```bash
cd backend
alembic upgrade head
```

This creates all tables (`business`, `yelp_user`, `review`, `tip`, `checkin`, `photo`) and enables the `pg_trgm` extension for fuzzy search.

### 5. Ingest the dataset

Ingestion takes a while. Run it in a `screen` session so it survives terminal disconnects:

```bash
screen -S ingest
cd backend
python scripts/ingest_dataset.py
```

Detach with `Ctrl+A D`. Reattach later with:

```bash
screen -r ingest
```

Ingestion order is FK-safe: `yelp_user → business → review → tip → checkin → photo`. Progress is printed per table. Commits every 100k rows to keep memory usage low.

### 6. Ingest photos

Photos live in a separate dataset file and have their own script:

```bash
cd backend
python scripts/ingest_photos.py
```

This reads `photos.json` from `YELP_PHOTO_DATASET_PATH` and bulk-inserts into the `photo` table using `psycopg2.extras.execute_values` (fast). Requires `pandas`:

```bash
uv pip install pandas
```

---

## Running the app

### Backend

```bash
cd backend
fastapi dev main.py
```

API available at `http://localhost:8000`. Docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

UI available at `http://localhost:5173`.

---

## API

### Search businesses

```
GET /businesses?city=Phoenix&name=pizza&scope=city&category=Mexican&min_stars=4.0&sort_by=relevance&order=desc&page=1&limit=20
```

| Param | Type | Default | Description |
|---|---|---|---|
| `city` | string | required | City to search — fuzzy matched with trigram |
| `name` | string | — | Optional business name filter — fuzzy matched |
| `scope` | `city` \| `radius` | `city` | `city` = trigram city filter, `radius` = geocoded 5-mile Haversine filter |
| `category` | string | — | Filter by category |
| `min_stars` | float | — | Minimum star rating |
| `sort_by` | `relevance` \| `stars` \| `review_count` \| `name` | `relevance` | Sort field |
| `order` | `asc` \| `desc` | `desc` | Sort direction |
| `page` | int | `1` | Page number |
| `limit` | int | `20` | Results per page |

---

## Running tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npx vitest run
```

---

## Architecture

### Backend

```
routes/          → FastAPI route definitions (thin, just wiring)
controllers/     → Request handlers (parse input, call services, build response)
services/        → Business logic (auth, search, geocoding)
  businesses.py  → Trigram search, Haversine distance filter
  geocoding.py   → Nominatim geocoding with in-memory cache
models.py        → SQLAlchemy ORM models
schema.py        → Pydantic request/response schemas
database.py      → SQLAlchemy engine + session factory
dependencies.py  → FastAPI Depends() providers
scripts/         → One-off scripts (dataset ingestion)
  ingest_dataset.py  → Ingests all main Yelp JSON files
  ingest_photos.py   → Ingests photos.json separately
```

### Frontend

```
src/
  components/    → SearchBar, FilterBar, ResultList, DetailPanel
  pages/         → SearchPage (main view)
  store/         → Zustand store (city, name, scope, filters, pagination)
  services/      → API calls (fetchBusinesses, fetchBusinessDetail)
  types/         → Shared TypeScript types
```

### Auth

JWT access token (15 min) in `Authorization` header + HttpOnly refresh token cookie (30 days). All `/businesses` endpoints are public — no auth required.

---

## Database migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1

# Generate a new migration from model changes
alembic revision --autogenerate -m "description"
```

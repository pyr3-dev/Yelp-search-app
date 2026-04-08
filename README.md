# Yelp Search App

Restaurant search app backed by the locally-downloaded Yelp Open Dataset. Users search by city with optional filters (category, stars, sort). FastAPI backend + PostgreSQL, React frontend (phase 2).

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package manager)
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
cp .env.example .env
```

Edit `backend/.env` and set `YELP_DATASET_PATH` to the folder containing the Yelp JSON files:

```
YELP_DATASET_PATH=/absolute/path/to/yelp_dataset
```

The other defaults work out of the box for the Docker setup.

### 4. Run database migrations

```bash
cd backend
alembic upgrade head
```

This creates all tables (`business`, `yelp_user`, `review`, `tip`, `checkin`, `photo`).

### 5. Ingest the dataset

The ingestion takes a while. Run it in a `screen` session so it survives terminal disconnects:

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

---

## Running the dev server

```bash
cd backend
fastapi dev main.py
```

API available at `http://localhost:8000`. Docs at `http://localhost:8000/docs`.

### Example search

```
GET /businesses?city=Phoenix&category=Mexican&min_stars=4.0&sort_by=stars&order=desc&page=1&limit=20
```

---

## Running tests

```bash
cd backend
pytest
```

---

## Architecture

```
routes/       → FastAPI route definitions (thin, just wiring)
controllers/  → Request handlers (parse input, call services, build response)
services/     → Business logic (auth, search, embedding, LLM)
models.py     → SQLAlchemy ORM models
schema.py     → Pydantic request/response schemas
database.py   → SQLAlchemy engine + session factory
dependencies.py → FastAPI Depends() providers
scripts/      → One-off scripts (dataset ingestion)
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

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Yelp-search-app is a restaurant search web app backed by the locally-downloaded Yelp Open Dataset. Users search by city with optional filters. The FastAPI backend ingests the dataset into PostgreSQL via Alembic migrations and exposes a REST API. A React frontend consumes the API.

## Commands

All commands run from `backend/` unless noted.

```bash
# Start PostgreSQL (run from repo root)
docker-compose up

# Install dependencies
uv pip install -e ".[dev]"

# Run dev server
fastapi dev main.py

# Run all tests
pytest

# Run a single test file
pytest tests/test_businesses.py -v

# Database migrations
alembic upgrade head
alembic downgrade -1
alembic revision --autogenerate -m "description"
```

## Environment Setup

Copy `backend/.env.example` to `backend/.env`. Key variables:

```
DATABASE_URL=postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/postgres
JWT_SECRET=...
REFRESH_SECRET=...
FRONTEND_URL=http://localhost:5173
YELP_DATASET_PATH=/path/to/yelp_dataset
```

Database: PostgreSQL 16 + pgvector via Docker (`pgvector/pgvector:pg16`, port 5432, user/pass: `postgres/postgres`).

## Architecture

```
routes/      → FastAPI route definitions (thin, just wiring)
controllers/ → Request handlers (parse input, call services, build response)
services/    → Business logic (auth, search, embedding, LLM, OpenAlex, user CRUD)
models.py    → SQLAlchemy ORM models
schema.py    → Pydantic request/response schemas
database.py  → SQLAlchemy engine + session factory
dependencies.py → FastAPI Depends() providers (db session, current user, embedding model)
```

### Request Flow

1. `routes/` → `controllers/` → `services/` → DB / external APIs
2. Auth: JWT access token (15 min) in Authorization header + HttpOnly refresh token cookie (30 days)
3. All `/businesses` endpoints are public (no auth required)

### Search & Filtering

`GET /businesses?city=Phoenix&category=Mexican&min_stars=4.0&sort_by=stars&order=desc&page=1&limit=20`

- City match is case-insensitive (`ilike`)
- Category filter uses PostgreSQL ARRAY contains: `categories @> ARRAY['category']`
- Sorts: `stars`, `review_count`, `name`

### Dataset Ingestion

Two Alembic migrations:
1. DDL migration: creates `business`, `yelp_user`, `review`, `tip`, `checkin`, `photo` tables
2. Data migration: streams `yelp_academic_dataset_*.json` files from `YELP_DATASET_PATH` in 1000-row batches using `INSERT ... ON CONFLICT DO NOTHING`

Ingestion order (FK-safe): yelp_user → business → review → tip → checkin → photo

### Auth

Optional — search endpoints are fully public. JWT auth system exists for future authenticated features. Existing `User` model and auth routes are untouched by the Yelp search work.

## State of the Codebase

- Auth system: complete (`routes/auth.py`, `controllers/auth.py`, `services/auth.py`, `services/user.py`)
- Business search API: to be implemented per `docs/superpowers/plans/2026-04-08-yelp-search-backend.md`
- Frontend: phase 2 (not yet started)

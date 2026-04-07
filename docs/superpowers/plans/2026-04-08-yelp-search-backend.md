# Yelp Search App — Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Yelp Open Dataset ingestion and a restaurant search REST API to the existing FastAPI backend.

**Architecture:** Six new SQLAlchemy models are added to `models.py` and created by an Alembic DDL migration. A second data migration streams each Yelp JSON file from `YELP_DATASET_PATH` into PostgreSQL in 1000-row batches using `INSERT ... ON CONFLICT DO NOTHING`. Four public REST endpoints under `/businesses` expose city search with filters, detail view, reviews, and photos.

**Tech Stack:** FastAPI 0.135+, SQLAlchemy 2, PostgreSQL 16 + pgvector, Alembic, psycopg2, pytest, FastAPI TestClient

---

## File Map

| Action | File | Responsibility |
|---|---|---|
| Modify | `backend/models.py` | Add Business, YelpUser, Review, Tip, Checkin, Photo |
| Modify | `backend/.env.example` | Add YELP_DATASET_PATH |
| Create | `backend/alembic/versions/XXXX_create_yelp_tables.py` | DDL: create all 6 tables + indexes |
| Create | `backend/alembic/versions/XXXX_ingest_yelp_dataset.py` | Data: stream JSON files into tables |
| Modify | `backend/schema.py` | Add request param + response schemas for /businesses |
| Create | `backend/services/businesses.py` | All DB query logic (search, detail, reviews, photos) |
| Create | `backend/controllers/businesses.py` | HTTP handlers for all 4 endpoints |
| Create | `backend/routes/businesses.py` | Route definitions |
| Modify | `backend/main.py` | Include businesses router |
| Create | `backend/tests/test_businesses.py` | API-level tests with mocked service |

---

### Task 1: Add models to models.py

**Files:**
- Modify: `backend/models.py`
- Test: `backend/tests/test_models.py`

- [ ] **Step 1: Write a failing import test**

Create `backend/tests/test_models.py`:

```python
def test_models_have_correct_tablenames():
    from models import Business, YelpUser, Review, Tip, Checkin, Photo

    assert Business.__tablename__ == "business"
    assert YelpUser.__tablename__ == "yelp_user"
    assert Review.__tablename__ == "review"
    assert Tip.__tablename__ == "tip"
    assert Checkin.__tablename__ == "checkin"
    assert Photo.__tablename__ == "photo"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/test_models.py -v
```

Expected: `ImportError: cannot import name 'Business' from 'models'`

- [ ] **Step 3: Replace models.py with the full content below**

```python
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.sql import func

from pgvector.sqlalchemy import Vector

from database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    email = Column(String(254), unique=True, index=True)
    password = Column(String(255))


class YelpUser(Base):
    __tablename__ = "yelp_user"

    user_id = Column(String(22), primary_key=True)
    name = Column(String)
    review_count = Column(Integer)
    yelping_since = Column(DateTime)
    average_stars = Column(Float)
    fans = Column(Integer)


class Business(Base):
    __tablename__ = "business"

    business_id = Column(String(22), primary_key=True)
    name = Column(String)
    address = Column(String)
    city = Column(String, index=True)
    state = Column(String(2))
    postal_code = Column(String(10))
    latitude = Column(Float)
    longitude = Column(Float)
    stars = Column(Float, index=True)
    review_count = Column(Integer, index=True)
    is_open = Column(Boolean)
    attributes = Column(JSONB)
    categories = Column(ARRAY(String))
    hours = Column(JSONB)


class Review(Base):
    __tablename__ = "review"

    review_id = Column(String(22), primary_key=True)
    user_id = Column(String(22))           # no FK — enforcing on 6.9M rows is too slow
    business_id = Column(String(22), ForeignKey("business.business_id"), index=True)
    stars = Column(SmallInteger)
    date = Column(DateTime)
    text = Column(Text)
    useful = Column(Integer)
    funny = Column(Integer)
    cool = Column(Integer)


class Tip(Base):
    __tablename__ = "tip"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text)
    date = Column(DateTime)
    compliment_count = Column(Integer)
    business_id = Column(String(22), ForeignKey("business.business_id"), index=True)
    user_id = Column(String(22))           # no FK


class Checkin(Base):
    __tablename__ = "checkin"

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(String(22), ForeignKey("business.business_id"), unique=True)
    dates = Column(Text)                   # comma-separated timestamps from dataset


class Photo(Base):
    __tablename__ = "photo"

    photo_id = Column(String(22), primary_key=True)
    business_id = Column(String(22), ForeignKey("business.business_id"), index=True)
    caption = Column(Text)
    label = Column(String(10))             # food/drink/menu/inside/outside
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_models.py -v
```

Expected: `PASSED`

- [ ] **Step 5: Commit**

```bash
git add backend/models.py backend/tests/test_models.py
git commit -m "feat: add Yelp dataset SQLAlchemy models"
```

---

### Task 2: Add YELP_DATASET_PATH env variable

**Files:**
- Modify: `backend/.env.example`
- Modify: `backend/.env`

- [ ] **Step 1: Add to .env.example**

Open `backend/.env.example`. Add at the bottom:

```
YELP_DATASET_PATH=/path/to/yelp_dataset
```

- [ ] **Step 2: Add the real path to your .env**

Open `backend/.env`. Add the actual path to where the Yelp dataset files live, e.g.:

```
YELP_DATASET_PATH=C:/Users/Joshua/Downloads/yelp_dataset
```

- [ ] **Step 3: Commit**

```bash
git add backend/.env.example
git commit -m "chore: add YELP_DATASET_PATH env variable"
```

---

### Task 3: DDL migration — create_yelp_tables

**Files:**
- Create: `backend/alembic/versions/XXXX_create_yelp_tables.py` (generated by alembic)

- [ ] **Step 1: Generate the migration skeleton**

```bash
cd backend
alembic revision -m "create_yelp_tables"
```

This creates a new file under `backend/alembic/versions/`. Note the filename (e.g., `abc123_create_yelp_tables.py`). Open it.

- [ ] **Step 2: Replace the file's entire contents with the following**

Replace `PREV_REVISION` with the revision ID of `954a910e0046_enable_pgvector.py` (i.e., `"954a910e0046"`), and `THIS_REVISION` with the auto-generated ID in the filename.

```python
"""create_yelp_tables

Revision ID: THIS_REVISION
Revises: 954a910e0046
Create Date: (keep the generated date)
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from alembic import op


revision: str = "THIS_REVISION"
down_revision: Union[str, Sequence[str], None] = "954a910e0046"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "yelp_user",
        sa.Column("user_id", sa.String(22), primary_key=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("review_count", sa.Integer(), nullable=True),
        sa.Column("yelping_since", sa.DateTime(), nullable=True),
        sa.Column("average_stars", sa.Float(), nullable=True),
        sa.Column("fans", sa.Integer(), nullable=True),
    )

    op.create_table(
        "business",
        sa.Column("business_id", sa.String(22), primary_key=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("city", sa.String(), nullable=True, index=True),
        sa.Column("state", sa.String(2), nullable=True),
        sa.Column("postal_code", sa.String(10), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("stars", sa.Float(), nullable=True, index=True),
        sa.Column("review_count", sa.Integer(), nullable=True, index=True),
        sa.Column("is_open", sa.Boolean(), nullable=True),
        sa.Column("attributes", JSONB(), nullable=True),
        sa.Column("categories", ARRAY(sa.String()), nullable=True),
        sa.Column("hours", JSONB(), nullable=True),
    )
    op.create_index(
        "ix_business_categories_gin",
        "business",
        ["categories"],
        postgresql_using="gin",
    )

    op.create_table(
        "review",
        sa.Column("review_id", sa.String(22), primary_key=True),
        sa.Column("user_id", sa.String(22), nullable=True),
        sa.Column(
            "business_id",
            sa.String(22),
            sa.ForeignKey("business.business_id"),
            nullable=True,
            index=True,
        ),
        sa.Column("stars", sa.SmallInteger(), nullable=True),
        sa.Column("date", sa.DateTime(), nullable=True),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("useful", sa.Integer(), nullable=True),
        sa.Column("funny", sa.Integer(), nullable=True),
        sa.Column("cool", sa.Integer(), nullable=True),
    )

    op.create_table(
        "tip",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("date", sa.DateTime(), nullable=True),
        sa.Column("compliment_count", sa.Integer(), nullable=True),
        sa.Column(
            "business_id",
            sa.String(22),
            sa.ForeignKey("business.business_id"),
            nullable=True,
            index=True,
        ),
        sa.Column("user_id", sa.String(22), nullable=True),
    )

    op.create_table(
        "checkin",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "business_id",
            sa.String(22),
            sa.ForeignKey("business.business_id"),
            nullable=True,
            unique=True,
        ),
        sa.Column("dates", sa.Text(), nullable=True),
    )

    op.create_table(
        "photo",
        sa.Column("photo_id", sa.String(22), primary_key=True),
        sa.Column(
            "business_id",
            sa.String(22),
            sa.ForeignKey("business.business_id"),
            nullable=True,
            index=True,
        ),
        sa.Column("caption", sa.Text(), nullable=True),
        sa.Column("label", sa.String(10), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("photo")
    op.drop_table("checkin")
    op.drop_table("tip")
    op.drop_table("review")
    op.drop_index("ix_business_categories_gin", table_name="business")
    op.drop_table("business")
    op.drop_table("yelp_user")
```

- [ ] **Step 3: Apply the migration**

```bash
cd backend
alembic upgrade head
```

Expected: migration runs without errors, tables visible in psql:
```bash
docker exec yelp_app_postgres_db psql -U postgres -c "\dt"
```
You should see: `business`, `yelp_user`, `review`, `tip`, `checkin`, `photo` in the list.

- [ ] **Step 4: Commit**

```bash
git add backend/alembic/versions/
git commit -m "feat: create Yelp dataset tables (DDL migration)"
```

---

### Task 4: Data migration — ingest_yelp_dataset

**Files:**
- Create: `backend/alembic/versions/XXXX_ingest_yelp_dataset.py` (generated by alembic)

The Yelp Open Dataset files are named `yelp_academic_dataset_business.json`, etc. Each file is newline-delimited JSON (one object per line).

- [ ] **Step 1: Generate the migration skeleton**

```bash
cd backend
alembic revision -m "ingest_yelp_dataset"
```

Open the generated file. Note its revision ID.

- [ ] **Step 2: Replace the file's entire contents with the following**

Replace `THIS_REVISION` with the auto-generated ID, and `PREV_REVISION` with the revision ID from Task 3.

```python
"""ingest_yelp_dataset

Revision ID: THIS_REVISION
Revises: PREV_REVISION (revision ID from Task 3)
Create Date: (keep the generated date)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Sequence, Union

from alembic import op

revision: str = "THIS_REVISION"
down_revision: Union[str, Sequence[str], None] = "PREV_REVISION"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

BATCH_SIZE = 1000


def _get_dataset_path() -> Path:
    dataset_path = os.environ.get("YELP_DATASET_PATH")
    if not dataset_path:
        raise RuntimeError(
            "YELP_DATASET_PATH environment variable is not set. "
            "Add it to backend/.env before running this migration."
        )
    path = Path(dataset_path)
    files = [
        "yelp_academic_dataset_user.json",
        "yelp_academic_dataset_business.json",
        "yelp_academic_dataset_review.json",
        "yelp_academic_dataset_tip.json",
        "yelp_academic_dataset_checkin.json",
        "yelp_academic_dataset_photo.json",
    ]
    missing = [f for f in files if not (path / f).exists()]
    if missing:
        raise RuntimeError(
            f"Missing dataset files in {path}:\n" + "\n".join(missing)
        )
    return path


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _ingest_users(bind, path: Path) -> None:
    print("Ingesting yelp_user...")
    batch, count = [], 0
    with open(path / "yelp_academic_dataset_user.json", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            batch.append({
                "user_id": row["user_id"],
                "name": row.get("name"),
                "review_count": row.get("review_count"),
                "yelping_since": _parse_date(row.get("yelping_since")),
                "average_stars": row.get("average_stars"),
                "fans": row.get("fans"),
            })
            if len(batch) >= BATCH_SIZE:
                bind.execute(
                    _upsert_sql("yelp_user", ["user_id", "name", "review_count",
                                              "yelping_since", "average_stars", "fans"]),
                    batch,
                )
                count += len(batch)
                batch = []
                if count % 100_000 == 0:
                    print(f"  yelp_user: {count:,} rows")
    if batch:
        bind.execute(
            _upsert_sql("yelp_user", ["user_id", "name", "review_count",
                                      "yelping_since", "average_stars", "fans"]),
            batch,
        )
        count += len(batch)
    print(f"  yelp_user done: {count:,} rows")


def _ingest_businesses(bind, path: Path) -> None:
    print("Ingesting business...")
    batch, count = [], 0
    with open(path / "yelp_academic_dataset_business.json", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            batch.append({
                "business_id": row["business_id"],
                "name": row.get("name"),
                "address": row.get("address"),
                "city": row.get("city"),
                "state": row.get("state"),
                "postal_code": row.get("postal_code"),
                "latitude": row.get("latitude"),
                "longitude": row.get("longitude"),
                "stars": row.get("stars"),
                "review_count": row.get("review_count"),
                "is_open": bool(row.get("is_open", 0)),
                "attributes": row.get("attributes"),
                "categories": [c.strip() for c in row["categories"].split(",")]
                               if row.get("categories") else [],
                "hours": row.get("hours"),
            })
            if len(batch) >= BATCH_SIZE:
                bind.execute(
                    _upsert_sql("business", ["business_id", "name", "address", "city",
                                             "state", "postal_code", "latitude", "longitude",
                                             "stars", "review_count", "is_open",
                                             "attributes", "categories", "hours"]),
                    batch,
                )
                count += len(batch)
                batch = []
    if batch:
        bind.execute(
            _upsert_sql("business", ["business_id", "name", "address", "city",
                                     "state", "postal_code", "latitude", "longitude",
                                     "stars", "review_count", "is_open",
                                     "attributes", "categories", "hours"]),
            batch,
        )
        count += len(batch)
    print(f"  business done: {count:,} rows")


def _ingest_reviews(bind, path: Path) -> None:
    print("Ingesting review (this may take a while)...")
    batch, count = [], 0
    with open(path / "yelp_academic_dataset_review.json", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            batch.append({
                "review_id": row["review_id"],
                "user_id": row.get("user_id"),
                "business_id": row.get("business_id"),
                "stars": row.get("stars"),
                "date": _parse_date(row.get("date")),
                "text": row.get("text"),
                "useful": row.get("useful"),
                "funny": row.get("funny"),
                "cool": row.get("cool"),
            })
            if len(batch) >= BATCH_SIZE:
                bind.execute(
                    _upsert_sql("review", ["review_id", "user_id", "business_id",
                                           "stars", "date", "text", "useful", "funny", "cool"]),
                    batch,
                )
                count += len(batch)
                batch = []
                if count % 100_000 == 0:
                    print(f"  review: {count:,} rows")
    if batch:
        bind.execute(
            _upsert_sql("review", ["review_id", "user_id", "business_id",
                                   "stars", "date", "text", "useful", "funny", "cool"]),
            batch,
        )
        count += len(batch)
    print(f"  review done: {count:,} rows")


def _ingest_tips(bind, path: Path) -> None:
    print("Ingesting tip...")
    batch, count = [], 0
    with open(path / "yelp_academic_dataset_tip.json", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            batch.append({
                "text": row.get("text"),
                "date": _parse_date(row.get("date")),
                "compliment_count": row.get("compliment_count"),
                "business_id": row.get("business_id"),
                "user_id": row.get("user_id"),
            })
            if len(batch) >= BATCH_SIZE:
                bind.execute(
                    _upsert_sql("tip", ["text", "date", "compliment_count",
                                        "business_id", "user_id"],
                                pk=None),
                    batch,
                )
                count += len(batch)
                batch = []
    if batch:
        bind.execute(
            _upsert_sql("tip", ["text", "date", "compliment_count",
                                "business_id", "user_id"],
                        pk=None),
            batch,
        )
        count += len(batch)
    print(f"  tip done: {count:,} rows")


def _ingest_checkins(bind, path: Path) -> None:
    print("Ingesting checkin...")
    batch, count = [], 0
    with open(path / "yelp_academic_dataset_checkin.json", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            batch.append({
                "business_id": row["business_id"],
                "dates": row.get("date", ""),
            })
            if len(batch) >= BATCH_SIZE:
                bind.execute(
                    _upsert_sql("checkin", ["business_id", "dates"],
                                conflict_col="business_id"),
                    batch,
                )
                count += len(batch)
                batch = []
    if batch:
        bind.execute(
            _upsert_sql("checkin", ["business_id", "dates"],
                        conflict_col="business_id"),
            batch,
        )
        count += len(batch)
    print(f"  checkin done: {count:,} rows")


def _ingest_photos(bind, path: Path) -> None:
    print("Ingesting photo...")
    batch, count = [], 0
    with open(path / "yelp_academic_dataset_photo.json", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            batch.append({
                "photo_id": row["photo_id"],
                "business_id": row.get("business_id"),
                "caption": row.get("caption"),
                "label": row.get("label"),
            })
            if len(batch) >= BATCH_SIZE:
                bind.execute(
                    _upsert_sql("photo", ["photo_id", "business_id", "caption", "label"]),
                    batch,
                )
                count += len(batch)
                batch = []
    if batch:
        bind.execute(
            _upsert_sql("photo", ["photo_id", "business_id", "caption", "label"]),
            batch,
        )
        count += len(batch)
    print(f"  photo done: {count:,} rows")


def _upsert_sql(table: str, columns: list[str], pk: str | None = None,
                conflict_col: str | None = None) -> str:
    """Build INSERT ... ON CONFLICT DO NOTHING SQL."""
    cols = ", ".join(columns)
    vals = ", ".join(f":{c}" for c in columns)
    if pk is None and conflict_col is None:
        # No PK — plain insert (tip uses auto-increment id)
        return f"INSERT INTO {table} ({cols}) VALUES ({vals})"
    conflict = conflict_col or columns[0]
    return (
        f"INSERT INTO {table} ({cols}) VALUES ({vals}) "
        f"ON CONFLICT ({conflict}) DO NOTHING"
    )


def upgrade() -> None:
    path = _get_dataset_path()
    bind = op.get_bind()

    _ingest_users(bind, path)
    _ingest_businesses(bind, path)
    _ingest_reviews(bind, path)
    _ingest_tips(bind, path)
    _ingest_checkins(bind, path)
    _ingest_photos(bind, path)

    print("Yelp dataset ingestion complete.")


def downgrade() -> None:
    bind = op.get_bind()
    for table in ["photo", "checkin", "tip", "review", "business", "yelp_user"]:
        bind.execute(f"DELETE FROM {table}")
```

- [ ] **Step 3: Run the migration**

```bash
cd backend
alembic upgrade head
```

This will take a while (review.json is ~6.9M rows). Progress is logged every 100k rows.

Verify row counts:
```bash
docker exec yelp_app_postgres_db psql -U postgres -c "
  SELECT 'business' AS t, COUNT(*) FROM business
  UNION ALL SELECT 'review', COUNT(*) FROM review
  UNION ALL SELECT 'yelp_user', COUNT(*) FROM yelp_user
  UNION ALL SELECT 'tip', COUNT(*) FROM tip
  UNION ALL SELECT 'checkin', COUNT(*) FROM checkin
  UNION ALL SELECT 'photo', COUNT(*) FROM photo;
"
```

- [ ] **Step 4: Commit**

```bash
git add backend/alembic/versions/
git commit -m "feat: ingest Yelp dataset via Alembic data migration"
```

---

### Task 5: Add Pydantic schemas

**Files:**
- Modify: `backend/schema.py`

- [ ] **Step 1: Add business schemas to the bottom of schema.py**

```python
from typing import Literal, Optional
from pydantic import ConfigDict


class BusinessResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    business_id: str
    name: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    stars: Optional[float]
    review_count: Optional[int]
    categories: Optional[list[str]]
    latitude: Optional[float]
    longitude: Optional[float]
    is_open: Optional[bool]


class TipResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: Optional[str]
    date: Optional[str]
    compliment_count: Optional[int]
    user_id: Optional[str]


class BusinessDetail(BusinessResult):
    attributes: Optional[dict]
    hours: Optional[dict]
    tips: list[TipResult] = []
    checkin_count: int = 0


class ReviewResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    review_id: str
    user_id: Optional[str]
    stars: Optional[int]
    date: Optional[str]
    text: Optional[str]
    useful: Optional[int]
    funny: Optional[int]
    cool: Optional[int]


class PhotoResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    photo_id: str
    caption: Optional[str]
    label: Optional[str]


class BusinessSearchResponse(BaseModel):
    total: int
    page: int
    limit: int
    results: list[BusinessResult]


class ReviewsResponse(BaseModel):
    total: int
    page: int
    limit: int
    results: list[ReviewResult]
```

- [ ] **Step 2: Verify import works**

```bash
cd backend
python -c "from schema import BusinessResult, BusinessDetail, ReviewResult, PhotoResult, BusinessSearchResponse, ReviewsResponse; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add backend/schema.py
git commit -m "feat: add Pydantic schemas for business endpoints"
```

---

### Task 6: Create services/businesses.py

**Files:**
- Create: `backend/services/businesses.py`
- Test: `backend/tests/test_businesses.py` (partial — add first tests now)

- [ ] **Step 1: Write failing tests for the service**

Create `backend/tests/test_businesses.py`:

```python
from unittest.mock import MagicMock, patch, PropertyMock


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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend
pytest tests/test_businesses.py -v
```

Expected: `ImportError: No module named 'services.businesses'`

- [ ] **Step 3: Create backend/services/businesses.py**

```python
from typing import Literal, Optional

from sqlalchemy.orm import Session

from models import Business, Checkin, Photo, Review, Tip


def search_businesses(
    db: Session,
    city: str,
    category: Optional[str] = None,
    min_stars: Optional[float] = None,
    sort_by: Literal["stars", "review_count", "name"] = "stars",
    order: Literal["asc", "desc"] = "desc",
    page: int = 1,
    limit: int = 20,
) -> tuple[list[Business], int]:
    query = db.query(Business).filter(
        Business.city.ilike(city)
    )
    if category:
        query = query.filter(Business.categories.contains([category]))
    if min_stars is not None:
        query = query.filter(Business.stars >= min_stars)

    total = query.count()

    sort_col = {
        "review_count": Business.review_count,
        "name": Business.name,
        "stars": Business.stars,
    }.get(sort_by, Business.stars)

    query = query.order_by(
        sort_col.asc() if order == "asc" else sort_col.desc()
    )
    results = query.offset((page - 1) * limit).limit(limit).all()
    return results, total


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

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_businesses.py -v
```

Expected: all 3 tests `PASSED`

- [ ] **Step 5: Commit**

```bash
git add backend/services/businesses.py backend/tests/test_businesses.py
git commit -m "feat: add businesses service with search, detail, reviews, photos"
```

---

### Task 7: Create controllers/businesses.py

**Files:**
- Create: `backend/controllers/businesses.py`

- [ ] **Step 1: Create the file**

```python
from typing import Annotated, Literal, Optional

from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dependencies import get_db
from schema import (
    BusinessDetail,
    BusinessSearchResponse,
    PhotoResult,
    ReviewResult,
    ReviewsResponse,
    TipResult,
)
from services.businesses import (
    get_business_detail,
    get_business_photos,
    get_business_reviews,
    search_businesses,
)


async def search_controller(
    city: Annotated[str, Query(description="City name (case-insensitive)")],
    category: Annotated[Optional[str], Query()] = None,
    min_stars: Annotated[Optional[float], Query(ge=0.0, le=5.0)] = None,
    sort_by: Annotated[Literal["stars", "review_count", "name"], Query()] = "stars",
    order: Annotated[Literal["asc", "desc"], Query()] = "desc",
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    db: Session = Depends(get_db),
) -> BusinessSearchResponse:
    results, total = search_businesses(
        db,
        city=city,
        category=category,
        min_stars=min_stars,
        sort_by=sort_by,
        order=order,
        page=page,
        limit=limit,
    )
    return BusinessSearchResponse(
        total=total,
        page=page,
        limit=limit,
        results=results,
    )


async def detail_controller(
    business_id: str,
    db: Session = Depends(get_db),
) -> BusinessDetail:
    result = get_business_detail(db, business_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Business not found")
    business, tips, checkin_count = result
    return BusinessDetail(
        **{c.name: getattr(business, c.name) for c in business.__table__.columns},
        tips=[TipResult.model_validate(t) for t in tips],
        checkin_count=checkin_count,
    )


async def reviews_controller(
    business_id: str,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    sort_by: Annotated[Literal["date", "stars"], Query()] = "date",
    order: Annotated[Literal["asc", "desc"], Query()] = "desc",
    db: Session = Depends(get_db),
) -> ReviewsResponse:
    results, total = get_business_reviews(
        db,
        business_id=business_id,
        page=page,
        limit=limit,
        sort_by=sort_by,
        order=order,
    )
    return ReviewsResponse(
        total=total,
        page=page,
        limit=limit,
        results=results,
    )


async def photos_controller(
    business_id: str,
    db: Session = Depends(get_db),
) -> list[PhotoResult]:
    photos = get_business_photos(db, business_id)
    return photos
```

- [ ] **Step 2: Verify import**

```bash
cd backend
python -c "from controllers.businesses import search_controller; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add backend/controllers/businesses.py
git commit -m "feat: add businesses controller"
```

---

### Task 8: Create routes and wire into main.py

**Files:**
- Create: `backend/routes/businesses.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Create backend/routes/businesses.py**

```python
from fastapi import APIRouter

from controllers.businesses import (
    detail_controller,
    photos_controller,
    reviews_controller,
    search_controller,
)

router = APIRouter(prefix="/businesses", tags=["businesses"])


@router.get("")
async def search(response=search_controller):
    return await search_controller.__wrapped__()


```

Actually, FastAPI doesn't use `__wrapped__`. Routes need to be written properly with Depends. Here's the correct pattern matching the existing `routes/auth.py`:

```python
from typing import Annotated, Literal, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from controllers.businesses import (
    detail_controller,
    photos_controller,
    reviews_controller,
    search_controller,
)
from dependencies import get_db
from schema import (
    BusinessDetail,
    BusinessSearchResponse,
    PhotoResult,
    ReviewsResponse,
)

router = APIRouter(prefix="/businesses", tags=["businesses"])


@router.get("", response_model=BusinessSearchResponse)
async def search(
    city: Annotated[str, Query()],
    category: Annotated[Optional[str], Query()] = None,
    min_stars: Annotated[Optional[float], Query(ge=0.0, le=5.0)] = None,
    sort_by: Annotated[Literal["stars", "review_count", "name"], Query()] = "stars",
    order: Annotated[Literal["asc", "desc"], Query()] = "desc",
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    db: Annotated[Session, Depends(get_db)] = None,
):
    return await search_controller(
        city=city,
        category=category,
        min_stars=min_stars,
        sort_by=sort_by,
        order=order,
        page=page,
        limit=limit,
        db=db,
    )


@router.get("/{business_id}", response_model=BusinessDetail)
async def detail(
    business_id: str,
    db: Annotated[Session, Depends(get_db)] = None,
):
    return await detail_controller(business_id=business_id, db=db)


@router.get("/{business_id}/reviews", response_model=ReviewsResponse)
async def reviews(
    business_id: str,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    sort_by: Annotated[Literal["date", "stars"], Query()] = "date",
    order: Annotated[Literal["asc", "desc"], Query()] = "desc",
    db: Annotated[Session, Depends(get_db)] = None,
):
    return await reviews_controller(
        business_id=business_id,
        page=page,
        limit=limit,
        sort_by=sort_by,
        order=order,
        db=db,
    )


@router.get("/{business_id}/photos", response_model=list[PhotoResult])
async def photos(
    business_id: str,
    db: Annotated[Session, Depends(get_db)] = None,
):
    return await photos_controller(business_id=business_id, db=db)
```

- [ ] **Step 2: Update main.py to include the businesses router**

Replace the contents of `backend/main.py` with:

```python
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.auth import router as auth_router
from routes.businesses import router as businesses_router

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(businesses_router)
```

- [ ] **Step 3: Verify the server starts**

```bash
cd backend
fastapi dev main.py
```

Expected: server starts, navigate to `http://127.0.0.1:8000/docs` — you should see `/businesses`, `/businesses/{business_id}`, `/businesses/{business_id}/reviews`, `/businesses/{business_id}/photos` in the Swagger UI.

Stop the server with Ctrl+C.

- [ ] **Step 4: Commit**

```bash
git add backend/routes/businesses.py backend/main.py
git commit -m "feat: add businesses routes and wire into app"
```

---

### Task 9: API-level tests

**Files:**
- Modify: `backend/tests/test_businesses.py`

- [ ] **Step 1: Add API tests to test_businesses.py**

Append the following to `backend/tests/test_businesses.py`:

```python
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app

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
    mock_biz = MagicMock(**_mock_business_dict())
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
```

- [ ] **Step 2: Run all tests**

```bash
cd backend
pytest tests/test_businesses.py tests/test_models.py -v
```

Expected: all tests `PASSED`

- [ ] **Step 3: Commit**

```bash
git add backend/tests/test_businesses.py
git commit -m "test: add API-level tests for businesses endpoints"
```

---

## Self-Review

**Spec coverage check:**
- ✅ Business, YelpUser, Review, Tip, Checkin, Photo models — Task 1
- ✅ YELP_DATASET_PATH env var — Task 2
- ✅ DDL migration — Task 3
- ✅ Data ingestion migration (streaming, batch 1000, ON CONFLICT DO NOTHING, progress logging) — Task 4
- ✅ Pydantic schemas for all endpoints — Task 5
- ✅ `GET /businesses` with city/category/min_stars/sort_by/order/page/limit — Tasks 6–8
- ✅ `GET /businesses/{id}` with tips (last 5) + checkin count — Tasks 6–8
- ✅ `GET /businesses/{id}/reviews` paginated — Tasks 6–8
- ✅ `GET /businesses/{id}/photos` — Tasks 6–8
- ✅ Auth untouched, businesses endpoints are public — Task 8
- ✅ Error raised if YELP_DATASET_PATH missing or files not found — Task 4

**Type consistency:**
- `search_businesses` signature in services.py matches usage in controllers.py ✅
- `get_business_detail` returns `tuple[Business, list[Tip], int]` — unpacked correctly in controller ✅
- `BusinessDetail` extends `BusinessResult` — inherits all fields ✅
- `TipResult.model_validate(t)` used in controller — matches Pydantic v2 API ✅

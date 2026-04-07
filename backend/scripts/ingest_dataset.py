"""
Yelp dataset ingestion script.

Streams all 6 Yelp Open Dataset JSON files into PostgreSQL in 1000-row batches.
Uses INSERT ... ON CONFLICT DO NOTHING — safe to re-run without duplication.

Usage (from backend/):
    python scripts/ingest_dataset.py

Requires:
    YELP_DATASET_PATH and DATABASE_URL set in backend/.env
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import sqlalchemy as sa
from dotenv import load_dotenv

# Load .env from backend/ directory
load_dotenv(Path(__file__).parent.parent / ".env")

BATCH_SIZE = 1000

DATASET_FILES = [
    "yelp_academic_dataset_user.json",
    "yelp_academic_dataset_business.json",
    "yelp_academic_dataset_review.json",
    "yelp_academic_dataset_tip.json",
    "yelp_academic_dataset_checkin.json",
    "yelp_academic_dataset_photo.json",
]


def _get_dataset_path() -> Path:
    dataset_path = os.environ.get("YELP_DATASET_PATH")
    if not dataset_path:
        raise RuntimeError(
            "YELP_DATASET_PATH is not set. Add it to backend/.env"
        )
    path = Path(dataset_path)
    missing = [f for f in DATASET_FILES if not (path / f).exists()]
    if missing:
        raise RuntimeError(
            f"Missing dataset files in {path}:\n" + "\n".join(missing)
        )
    return path


def _get_engine() -> sa.Engine:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set. Add it to backend/.env")
    return sa.create_engine(database_url)


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _upsert_sql(table: str, columns: list[str], conflict_col: str | None = None) -> str:
    cols = ", ".join(columns)
    vals = ", ".join(f":{c}" for c in columns)
    if conflict_col is None:
        return f"INSERT INTO {table} ({cols}) VALUES ({vals})"
    return (
        f"INSERT INTO {table} ({cols}) VALUES ({vals}) "
        f"ON CONFLICT ({conflict_col}) DO NOTHING"
    )


def _ingest_users(conn, path: Path) -> None:
    print("Ingesting yelp_user...")
    sql = sa.text(_upsert_sql(
        "yelp_user",
        ["user_id", "name", "review_count", "yelping_since", "average_stars", "fans"],
        conflict_col="user_id",
    ))
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
                conn.execute(sql, batch)
                count += len(batch)
                batch = []
                if count % 100_000 == 0:
                    print(f"  yelp_user: {count:,} rows")
    if batch:
        conn.execute(sql, batch)
        count += len(batch)
    print(f"  yelp_user done: {count:,} rows")


def _ingest_businesses(conn, path: Path) -> None:
    print("Ingesting business...")
    cols = ["business_id", "name", "address", "city", "state", "postal_code",
            "latitude", "longitude", "stars", "review_count", "is_open",
            "attributes", "categories", "hours"]
    sql = sa.text(_upsert_sql("business", cols, conflict_col="business_id"))
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
                conn.execute(sql, batch)
                count += len(batch)
                batch = []
                if count % 100_000 == 0:
                    print(f"  business: {count:,} rows")
    if batch:
        conn.execute(sql, batch)
        count += len(batch)
    print(f"  business done: {count:,} rows")


def _ingest_reviews(conn, path: Path) -> None:
    print("Ingesting review (this may take a while)...")
    cols = ["review_id", "user_id", "business_id", "stars", "date", "text",
            "useful", "funny", "cool"]
    sql = sa.text(_upsert_sql("review", cols, conflict_col="review_id"))
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
                conn.execute(sql, batch)
                count += len(batch)
                batch = []
                if count % 100_000 == 0:
                    print(f"  review: {count:,} rows")
    if batch:
        conn.execute(sql, batch)
        count += len(batch)
    print(f"  review done: {count:,} rows")


def _ingest_tips(conn, path: Path) -> None:
    print("Ingesting tip...")
    cols = ["text", "date", "compliment_count", "business_id", "user_id"]
    sql = sa.text(_upsert_sql("tip", cols, conflict_col=None))
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
                conn.execute(sql, batch)
                count += len(batch)
                batch = []
    if batch:
        conn.execute(sql, batch)
        count += len(batch)
    print(f"  tip done: {count:,} rows")


def _ingest_checkins(conn, path: Path) -> None:
    print("Ingesting checkin...")
    sql = sa.text(_upsert_sql("checkin", ["business_id", "dates"], conflict_col="business_id"))
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
                conn.execute(sql, batch)
                count += len(batch)
                batch = []
    if batch:
        conn.execute(sql, batch)
        count += len(batch)
    print(f"  checkin done: {count:,} rows")


def _ingest_photos(conn, path: Path) -> None:
    print("Ingesting photo...")
    sql = sa.text(_upsert_sql("photo", ["photo_id", "business_id", "caption", "label"],
                              conflict_col="photo_id"))
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
                conn.execute(sql, batch)
                count += len(batch)
                batch = []
    if batch:
        conn.execute(sql, batch)
        count += len(batch)
    print(f"  photo done: {count:,} rows")


def main() -> None:
    path = _get_dataset_path()
    engine = _get_engine()

    with engine.connect() as conn:
        _ingest_users(conn, path)
        _ingest_businesses(conn, path)
        _ingest_reviews(conn, path)
        _ingest_tips(conn, path)
        _ingest_checkins(conn, path)
        _ingest_photos(conn, path)
        conn.commit()

    print("Yelp dataset ingestion complete.")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

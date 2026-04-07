"""
Yelp dataset ingestion script — pandas + execute_values edition.

Uses pd.read_json(lines=True, chunksize=N) for fast C-based JSON parsing
and psycopg2.extras.execute_values for bulk inserts (~5-10x faster than
the previous row-by-row approach).

Usage (from backend/):
    python scripts/ingest_dataset.py

Requires:
    YELP_DATASET_PATH and DATABASE_URL set in backend/.env
    pandas installed: uv pip install pandas
"""

import os
import sys
from pathlib import Path

import pandas as pd
import psycopg2
import psycopg2.extensions
import psycopg2.extras
import sqlalchemy as sa
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# Automatically serialize Python dicts as JSON for JSONB columns
psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)

CHUNK_SIZE = 50_000

REQUIRED_FILES = [
    "yelp_academic_dataset_user.json",
    "yelp_academic_dataset_business.json",
    "yelp_academic_dataset_review.json",
    "yelp_academic_dataset_tip.json",
    "yelp_academic_dataset_checkin.json",
]


def _get_dataset_path() -> Path:
    dataset_path = os.environ.get("YELP_DATASET_PATH")
    if not dataset_path:
        raise RuntimeError("YELP_DATASET_PATH is not set. Add it to backend/.env")
    path = Path(dataset_path)
    missing = [f for f in REQUIRED_FILES if not (path / f).exists()]
    if missing:
        raise RuntimeError(
            f"Missing dataset files in {path}:\n" + "\n".join(missing)
        )
    return path


def _get_conn(database_url: str):
    engine = sa.create_engine(database_url)
    return engine.raw_connection()


def _rows(df: pd.DataFrame) -> list[tuple]:
    """Convert DataFrame to tuples, replacing NaN/NaT with None."""
    return list(df.astype(object).where(pd.notna(df), None).itertuples(index=False, name=None))


COMMIT_EVERY = 100_000


def _commit_if_due(conn, count: int, label: str) -> None:
    if count % COMMIT_EVERY == 0:
        conn.commit()
        print(f"  {label}: {count:,} rows (committed)")


def ingest_users(conn, cursor, path: Path) -> None:
    print("Ingesting yelp_user...")
    sql = """
        INSERT INTO yelp_user (user_id, name, review_count, yelping_since, average_stars, fans)
        VALUES %s ON CONFLICT (user_id) DO NOTHING
    """
    cols = ["user_id", "name", "review_count", "yelping_since", "average_stars", "fans"]
    count = 0
    for chunk in pd.read_json(path / "yelp_academic_dataset_user.json", lines=True, chunksize=CHUNK_SIZE):
        chunk = chunk[cols].copy()
        chunk["yelping_since"] = pd.to_datetime(chunk["yelping_since"], errors="coerce")
        psycopg2.extras.execute_values(cursor, sql, _rows(chunk), page_size=5000)
        count += len(chunk)
        _commit_if_due(conn, count, "yelp_user")
    conn.commit()
    print(f"  yelp_user done: {count:,} rows")


def ingest_businesses(conn, cursor, path: Path) -> None:
    print("Ingesting business...")
    sql = """
        INSERT INTO business (
            business_id, name, address, city, state, postal_code,
            latitude, longitude, stars, review_count, is_open,
            attributes, categories, hours
        ) VALUES %s ON CONFLICT (business_id) DO NOTHING
    """
    cols = ["business_id", "name", "address", "city", "state", "postal_code",
            "latitude", "longitude", "stars", "review_count", "is_open",
            "attributes", "categories", "hours"]
    count = 0
    for chunk in pd.read_json(path / "yelp_academic_dataset_business.json", lines=True, chunksize=CHUNK_SIZE):
        chunk = chunk.reindex(columns=cols).copy()
        chunk["categories"] = chunk["categories"].apply(
            lambda x: [c.strip() for c in x.split(",")] if isinstance(x, str) and x else []
        )
        chunk["state"] = chunk["state"].str[:2]
        chunk["is_open"] = chunk["is_open"].fillna(0).astype(bool)
        psycopg2.extras.execute_values(cursor, sql, _rows(chunk), page_size=5000)
        count += len(chunk)
        _commit_if_due(conn, count, "business")
    conn.commit()
    print(f"  business done: {count:,} rows")


def ingest_reviews(conn, cursor, path: Path) -> None:
    print("Ingesting review (this may take a while)...")
    sql = """
        INSERT INTO review (review_id, user_id, business_id, stars, date, text, useful, funny, cool)
        VALUES %s ON CONFLICT (review_id) DO NOTHING
    """
    cols = ["review_id", "user_id", "business_id", "stars", "date", "text", "useful", "funny", "cool"]
    count = 0
    for chunk in pd.read_json(path / "yelp_academic_dataset_review.json", lines=True, chunksize=CHUNK_SIZE):
        chunk = chunk[cols].copy()
        chunk["date"] = pd.to_datetime(chunk["date"], errors="coerce")
        psycopg2.extras.execute_values(cursor, sql, _rows(chunk), page_size=5000)
        count += len(chunk)
        _commit_if_due(conn, count, "review")
    conn.commit()
    print(f"  review done: {count:,} rows")


def ingest_tips(conn, cursor, path: Path) -> None:
    print("Ingesting tip...")
    sql = """
        INSERT INTO tip (text, date, compliment_count, business_id, user_id)
        VALUES %s ON CONFLICT DO NOTHING
    """
    cols = ["text", "date", "compliment_count", "business_id", "user_id"]
    count = 0
    for chunk in pd.read_json(path / "yelp_academic_dataset_tip.json", lines=True, chunksize=CHUNK_SIZE):
        chunk = chunk[cols].copy()
        chunk["date"] = pd.to_datetime(chunk["date"], errors="coerce")
        psycopg2.extras.execute_values(cursor, sql, _rows(chunk), page_size=5000)
        count += len(chunk)
        _commit_if_due(conn, count, "tip")
    conn.commit()
    print(f"  tip done: {count:,} rows")


def ingest_checkins(conn, cursor, path: Path) -> None:
    print("Ingesting checkin...")
    sql = """
        INSERT INTO checkin (business_id, dates)
        VALUES %s ON CONFLICT (business_id) DO NOTHING
    """
    count = 0
    for chunk in pd.read_json(path / "yelp_academic_dataset_checkin.json", lines=True, chunksize=CHUNK_SIZE):
        chunk = chunk.rename(columns={"date": "dates"})[["business_id", "dates"]].copy()
        chunk["dates"] = chunk["dates"].fillna("")
        psycopg2.extras.execute_values(cursor, sql, _rows(chunk), page_size=5000)
        count += len(chunk)
        _commit_if_due(conn, count, "checkin")
    conn.commit()
    print(f"  checkin done: {count:,} rows")


def ingest_photos(conn, cursor, path: Path) -> None:
    photo_file = path / "yelp_academic_dataset_photo.json"
    if not photo_file.exists():
        print("  photo: file not found, skipping")
        return
    print("Ingesting photo...")
    sql = """
        INSERT INTO photo (photo_id, business_id, caption, label)
        VALUES %s ON CONFLICT (photo_id) DO NOTHING
    """
    cols = ["photo_id", "business_id", "caption", "label"]
    count = 0
    for chunk in pd.read_json(photo_file, lines=True, chunksize=CHUNK_SIZE):
        chunk = chunk[cols].copy()
        psycopg2.extras.execute_values(cursor, sql, _rows(chunk), page_size=5000)
        count += len(chunk)
        _commit_if_due(conn, count, "photo")
    conn.commit()
    print(f"  photo done: {count:,} rows")


def main() -> None:
    path = _get_dataset_path()
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set. Add it to backend/.env")

    conn = _get_conn(database_url)
    cursor = conn.cursor()
    ingest_users(conn, cursor, path)
    ingest_businesses(conn, cursor, path)
    ingest_reviews(conn, cursor, path)
    ingest_tips(conn, cursor, path)
    ingest_checkins(conn, cursor, path)
    ingest_photos(conn, cursor, path)
    cursor.close()
    conn.close()

    print("Yelp dataset ingestion complete.")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

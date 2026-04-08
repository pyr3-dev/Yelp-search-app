"""
Yelp photos dataset ingestion script — pandas + execute_values edition.

Uses pd.read_json(lines=True, chunksize=N) for fast C-based JSON parsing
and psycopg2.extras.execute_values for bulk inserts (~5-10x faster than
the previous row-by-row approach).

Usage (from backend/):
    python scripts/ingest_photos.py

Requires:
    YELP_PHOTO_DATASET_PATH and DATABASE_URL set in backend/.env
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
    "photos.json",
]


def _get_dataset_path() -> Path:
    dataset_path = os.environ.get("YELP_PHOTO_DATASET_PATH")
    if not dataset_path:
        raise RuntimeError("YELP_PHOTO_DATASET_PATH is not set. Add it to backend/.env")
    path = Path(dataset_path)
    missing = [f for f in REQUIRED_FILES if not (path / f).exists()]
    if missing:
        raise RuntimeError(f"Missing dataset files in {path}:\n" + "\n".join(missing))
    return path


def _get_conn(database_url: str):
    engine = sa.create_engine(database_url)
    return engine.raw_connection()


def _rows(df: pd.DataFrame) -> list[tuple]:
    """Convert DataFrame to tuples, replacing NaN/NaT with None."""
    return list(
        df.astype(object).where(pd.notna(df), None).itertuples(index=False, name=None)
    )


COMMIT_EVERY = 100_000


def _commit_if_due(conn, count: int, label: str) -> None:
    if count % COMMIT_EVERY == 0:
        conn.commit()
        print(f"  {label}: {count:,} rows (committed)")


def ingest_photos(conn, cursor, path: Path) -> None:
    photo_file = path / "photos.json"
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

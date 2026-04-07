"""ingest_yelp_dataset

Revision ID: 2e9263df2299
Revises: ff2141bac104
Create Date: 2026-04-08 05:51:10.960850

"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "2e9263df2299"
down_revision: Union[str, Sequence[str], None] = "ff2141bac104"
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
                    sa.text(_upsert_sql("yelp_user", ["user_id", "name", "review_count",
                                              "yelping_since", "average_stars", "fans"])),
                    batch,
                )
                count += len(batch)
                batch = []
                if count % 100_000 == 0:
                    print(f"  yelp_user: {count:,} rows")
    if batch:
        bind.execute(
            sa.text(_upsert_sql("yelp_user", ["user_id", "name", "review_count",
                                      "yelping_since", "average_stars", "fans"])),
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
                    sa.text(_upsert_sql("business", ["business_id", "name", "address", "city",
                                             "state", "postal_code", "latitude", "longitude",
                                             "stars", "review_count", "is_open",
                                             "attributes", "categories", "hours"])),
                    batch,
                )
                count += len(batch)
                batch = []
    if batch:
        bind.execute(
            sa.text(_upsert_sql("business", ["business_id", "name", "address", "city",
                                     "state", "postal_code", "latitude", "longitude",
                                     "stars", "review_count", "is_open",
                                     "attributes", "categories", "hours"])),
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
                    sa.text(_upsert_sql("review", ["review_id", "user_id", "business_id",
                                           "stars", "date", "text", "useful", "funny", "cool"])),
                    batch,
                )
                count += len(batch)
                batch = []
                if count % 100_000 == 0:
                    print(f"  review: {count:,} rows")
    if batch:
        bind.execute(
            sa.text(_upsert_sql("review", ["review_id", "user_id", "business_id",
                                   "stars", "date", "text", "useful", "funny", "cool"])),
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
                    sa.text(_upsert_sql("tip", ["text", "date", "compliment_count",
                                        "business_id", "user_id"],
                                pk=None)),
                    batch,
                )
                count += len(batch)
                batch = []
    if batch:
        bind.execute(
            sa.text(_upsert_sql("tip", ["text", "date", "compliment_count",
                                "business_id", "user_id"],
                        pk=None)),
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
                    sa.text(_upsert_sql("checkin", ["business_id", "dates"],
                                conflict_col="business_id")),
                    batch,
                )
                count += len(batch)
                batch = []
    if batch:
        bind.execute(
            sa.text(_upsert_sql("checkin", ["business_id", "dates"],
                        conflict_col="business_id")),
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
                    sa.text(_upsert_sql("photo", ["photo_id", "business_id", "caption", "label"])),
                    batch,
                )
                count += len(batch)
                batch = []
    if batch:
        bind.execute(
            sa.text(_upsert_sql("photo", ["photo_id", "business_id", "caption", "label"])),
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
        bind.execute(sa.text(f"DELETE FROM {table}"))

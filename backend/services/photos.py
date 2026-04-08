import os
from pathlib import Path


def get_photo_path(photo_id: str) -> Path | None:
    dataset_path = os.getenv("YELP_PHOTO_DATASET_PATH")
    if not dataset_path:
        return None
    path = Path(dataset_path) / "photos" / f"{photo_id}.jpg"
    return path if path.is_file() else None

import math
from typing import Literal, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models import Business, Checkin, Photo, Review, Tip

SIMILARITY_THRESHOLD = 0.3


def search_businesses(
    db: Session,
    city: str,
    category: Optional[str] = None,
    min_stars: Optional[float] = None,
    name: Optional[str] = None,
    scope: Literal["city", "radius"] = "city",
    sort_by: Literal["relevance", "stars", "review_count", "name"] = "relevance",
    order: Literal["asc", "desc"] = "desc",
    page: int = 1,
    limit: int = 20,
) -> tuple[list[tuple[Business, str | None]], int]:
    if scope == "radius":
        from services.geocoding import geocode_city, haversine_miles_expr
        canonical = (
            db.query(Business.city)
            .filter(func.similarity(Business.city, city) > SIMILARITY_THRESHOLD)
            .order_by(func.similarity(Business.city, city).desc())
            .limit(1)
            .scalar()
        )
        if canonical is None:
            return [], 0
        center_lat, center_lon = geocode_city(canonical)
        distance_expr = haversine_miles_expr(center_lat, center_lon)
        query = db.query(Business).filter(distance_expr <= 5.0)
    else:
        query = db.query(Business).filter(
            func.similarity(Business.city, city) > SIMILARITY_THRESHOLD
        )

    if name:
        query = query.filter(
            func.similarity(Business.name, name) > SIMILARITY_THRESHOLD
        )
    if category:
        query = query.filter(Business.categories.contains([category]))
    if min_stars is not None:
        query = query.filter(Business.stars >= min_stars)

    total = query.count()

    if sort_by == "relevance":
        city_sim = func.similarity(Business.city, city)
        relevance = (
            (city_sim + func.similarity(Business.name, name)) / 2
            if name
            else city_sim
        )
        sort_expr = relevance.desc() if order == "desc" else relevance.asc()
    else:
        sort_col = {
            "review_count": Business.review_count,
            "name": Business.name,
            "stars": Business.stars,
        }.get(sort_by, Business.stars)
        sort_expr = sort_col.asc() if order == "asc" else sort_col.desc()

    first_photo_subq = (
        select(Photo.photo_id)
        .where(Photo.business_id == Business.business_id)
        .limit(1)
        .correlate(Business)
        .scalar_subquery()
    )

    rows = (
        query.order_by(sort_expr)
        .add_columns(first_photo_subq.label("first_photo_id"))
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return [(row[0], row[1]) for row in rows], total


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

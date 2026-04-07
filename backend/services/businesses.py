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

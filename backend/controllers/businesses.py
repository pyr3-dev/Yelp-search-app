from typing import Annotated, Literal, Optional

from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dependencies import get_db
from schema import (
    BusinessDetail,
    BusinessSearchResponse,
    PhotoResult,
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
    city: Annotated[str, Query(description="City name")],
    category: Annotated[Optional[str], Query()] = None,
    min_stars: Annotated[Optional[float], Query(ge=0.0, le=5.0)] = None,
    name: Annotated[Optional[str], Query()] = None,
    scope: Annotated[Literal["city", "radius"], Query()] = "city",
    sort_by: Annotated[
        Literal["relevance", "stars", "review_count", "name"], Query()
    ] = "relevance",
    order: Annotated[Literal["asc", "desc"], Query()] = "desc",
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    db: Session = Depends(get_db),
) -> BusinessSearchResponse:
    try:
        rows, total = search_businesses(
            db,
            city=city,
            category=category,
            min_stars=min_stars,
            name=name,
            scope=scope,
            sort_by=sort_by,
            order=order,
            page=page,
            limit=limit,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    results = [
        BusinessDetail(
            **{c.name: getattr(business, c.name) for c in business.__table__.columns},
            first_photo_id=first_photo_id,
        )
        for business, first_photo_id in rows
    ]
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

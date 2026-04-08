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
    name: Annotated[Optional[str], Query()] = None,
    scope: Annotated[Literal["city", "radius"], Query()] = "city",
    sort_by: Annotated[
        Literal["relevance", "stars", "review_count", "name"], Query()
    ] = "relevance",
    order: Annotated[Literal["asc", "desc"], Query()] = "desc",
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    db: Annotated[Session, Depends(get_db)] = None,
):
    return await search_controller(
        city=city,
        category=category,
        min_stars=min_stars,
        name=name,
        scope=scope,
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

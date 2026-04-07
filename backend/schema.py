from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    id: int
    email: str
    password: str


class RegisterForm(BaseModel):
    email: str
    password: str


class Config:
    orm_mode = True


class BusinessResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    business_id: str
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    stars: Optional[float] = None
    review_count: Optional[int] = None
    categories: Optional[list[str]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_open: Optional[bool] = None


class TipResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: Optional[str] = None
    date: Optional[datetime] = None
    compliment_count: Optional[int] = None
    user_id: Optional[str] = None


class BusinessDetail(BusinessResult):
    attributes: Optional[dict] = None
    hours: Optional[dict] = None
    tips: list[TipResult] = []
    checkin_count: int = 0


class ReviewResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    review_id: str
    user_id: Optional[str] = None
    stars: Optional[int] = None
    date: Optional[datetime] = None
    text: Optional[str] = None
    useful: Optional[int] = None
    funny: Optional[int] = None
    cool: Optional[int] = None


class PhotoResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    photo_id: str
    caption: Optional[str] = None
    label: Optional[str] = None


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

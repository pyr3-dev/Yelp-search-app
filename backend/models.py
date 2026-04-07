from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

from pgvector.sqlalchemy import Vector  # noqa: F401 — reserved for future embedding column

from database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    email = Column(String(254), unique=True, index=True)
    password = Column(String(255))


class YelpUser(Base):
    __tablename__ = "yelp_user"

    user_id = Column(String(22), primary_key=True)
    name = Column(String)
    review_count = Column(Integer)
    yelping_since = Column(DateTime)
    average_stars = Column(Float)
    fans = Column(Integer)


class Business(Base):
    __tablename__ = "business"

    business_id = Column(String(22), primary_key=True)
    name = Column(String)
    address = Column(String)
    city = Column(String, index=True)
    state = Column(String(2))
    postal_code = Column(String(10))
    latitude = Column(Float)
    longitude = Column(Float)
    stars = Column(Float, index=True)
    review_count = Column(Integer, index=True)
    is_open = Column(Boolean)
    attributes = Column(JSONB)
    categories = Column(ARRAY(String))
    hours = Column(JSONB)


class Review(Base):
    __tablename__ = "review"

    review_id = Column(String(22), primary_key=True)
    user_id = Column(String(22))           # no FK — enforcing on 6.9M rows is too slow
    business_id = Column(String(22), ForeignKey("business.business_id"), index=True)
    stars = Column(SmallInteger)
    date = Column(DateTime)
    text = Column(Text)
    useful = Column(Integer)
    funny = Column(Integer)
    cool = Column(Integer)


class Tip(Base):
    __tablename__ = "tip"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text)
    date = Column(DateTime)
    compliment_count = Column(Integer)
    business_id = Column(String(22), ForeignKey("business.business_id"), index=True)
    user_id = Column(String(22))           # no FK


class Checkin(Base):
    __tablename__ = "checkin"

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(String(22), ForeignKey("business.business_id"), unique=True)
    dates = Column(Text)                   # comma-separated timestamps from dataset


class Photo(Base):
    __tablename__ = "photo"

    photo_id = Column(String(22), primary_key=True)
    business_id = Column(String(22), ForeignKey("business.business_id"), index=True)
    caption = Column(Text)
    label = Column(String(10))             # food/drink/menu/inside/outside

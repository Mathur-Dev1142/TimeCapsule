from sqlalchemy import (
    Column, Integer, String, Date, Float,Text, Enum, UniqueConstraint, Index
)

from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()   

class Region(str, enum.Enum):
    india = "India"
    world = "world"


class Category(str, enum.Enum):
    politics = "politics"
    sports = "sports"
    economy = "economy"
    culture = "culture"
    weather = "weather"
    other = "other"

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    event_date = Column(Date, nullable = False)
    day = Column(Integer, nullable = False)
    month = Column(Integer, nullable = False)
    year = Column(Integer, nullable=True)
    region = Column(Enum(Region), nullable = False)
    category = Column(Enum(Category), nullable = False, default=Category.other)
    title = Column(String(300), nullable = False)
    summary = Column(Text, nullable = True)
    source_url = Column(String(500), nullable = True)
    significance_score = Column(Integer, nullable = True, default=0)

    __table_args__ = (
        Index("ix_events_month_day", "month", "day"),
        Index("ix_events_year_region", "year", "region"),
    )

class WeatherCache(Base):
    __tablename__ = "weather_cache"

    id = Column(Integer, primary_key=True)
    cache_date = Column(Date, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    temperature_c = Column(Float, nullable=True)
    conditions = Column(String(100), nullable=True)

    __table_args__ = (
        UniqueConstraint("cache_date", "latitude", "longitude", name = "uq_weather_lookup"),
    )


class PriceReference(Base):
    __tablename__ = "price_reference"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)
    item = Column(String(100), nullable=False)      # e.g. "petrol", "gold", "milk"
    price_inr = Column(Float, nullable=False)
    unit = Column(String(50), nullable=True)          # e.g. "per litre", "per 10g"

    __table_args__ = (
        UniqueConstraint("year", "item", name="uq_price_year_item"),
    )





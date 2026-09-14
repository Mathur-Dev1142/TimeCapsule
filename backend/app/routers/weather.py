from datetime import date
from fastapi import APIRouter,  Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.weather import save_weather
from app.constants import DEFAULT_COORDINATES

router = APIRouter()

@router.get("/weather")
def get_weather(region : str, date_str: str, db: Session = Depends(get_db)):
    coords = DEFAULT_COORDINATES.get(region.lower())
    if not coords:
        return {"error": f"Unknown region '{region}'. Use 'india' or 'world'."}

    year , month , day = map(int, date_str.split("-"))
    event_date = date(year , month , day)

    result = save_weather(db, coords["latitude"] , coords["longitude"], event_date)
    return result
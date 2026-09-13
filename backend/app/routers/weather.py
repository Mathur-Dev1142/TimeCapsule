from datetime import date
from fastapi import APIRouter,  Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.weather import save_weather

router = APIRouter()

@router.get("/weather")
def get_weather(latitude : float, longitude: float, date_str: str, db: Session = Depends(get_db)):
    year , month , day = map(int, date_str.split("-"))
    event_date = date(year , month , day)
    result = save_weather(db, latitude , longitude, event_date)
    return result
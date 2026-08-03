from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Event, Region
from app.services.wikipedia import save_world_events
from app.services.india_events import save_india_events


router = APIRouter()

@router.get("/events/world")
def get_world_events(month: int, day: int, db: Session = Depends(get_db)):
    saved = save_world_events(db,month,day)
    return {"month": month, "day": day, "new_events_saved": saved}

@router.get("/events/india")
def get_india_events(year: int, db: Session = Depends(get_db)):
    saved = save_india_events(db , year)
    return {"year": year, "new_events_saved": saved}

@router.get("/events/world/list")
def list_world_events(month: int, day: int, db: Session = Depends(get_db)):
    events = (
        db.query(Event)
        .filter(Event.month == month , Event.day == day, Event.region == Region.world)
        .order_by(Event.year)
        .all()
    )
    return [
        {
            "title" : e.title,
            "year" : e.year,
            "source_url" : e.source_url,
        }
        for e in events
    ]


@router.get("/events/india/list")
def list_india_events(year:int, db:Session = Depends(get_db)):
    events = (
        db.query(Event)
        .filter(Event.year == year, Event.region == Region.india)
        .order_by(Event.month, Event.day)
        .all()
    )
    return [
        {
            "title" : e.title,
            "month" : e.month,
            "day" : e.day,
            "source_url" : e.source_url,
        }
        for e in events
    ]
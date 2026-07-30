from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.wikipedia import save_world_events

router = APIRouter()

@router.get("/events/world")
def get_world_events(month: int, day: int, db: Session = Depends(get_db)):
    saved = save_world_events(db,month,day)
    return {"month": month, "day": day, "new_events_saved": saved}
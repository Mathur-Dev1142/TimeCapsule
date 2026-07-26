import os
import httpx
from datetime import date
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from app.models import Event , Region , Category

load_dotenv()

WIKIMEDIA_TOKEN = os.environ["WIKIMEDIA_ACCESS_TOKEN"]

HEADERS = {
    "Authorization": f"Bearer {WIKIMEDIA_TOKEN}",
    "User-Agent": "TimeCapsule/1.0(deepmat465@gmail.com)"
}

def fetch_world_events(month: int, day: int) -> list[dict]:
    """Call Wikimedia's on-this-day feed for a given month/day."""
    month_str = f"{month:02d}"
    day_str = f"{day:02d}"
    url = f"https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/all/{month_str}/{day_str}"

    response = httpx.get(url,headers=HEADERS, timeout=30.0)
    response.raise_for_status()
    data = response.json()

    return data.get("events",[])

def save_world_events(db:Session, month:int , day:int) -> int:
    """Fetch events for a date and save any new ones to database."""
    raw_events = fetch_world_events(month,day)
    saved_count = 0

    for item in raw_events:
        year = item.get("year")
        title = item.get("text", "")[:300]

        exists = (
            db.query(Event)
            .filter(Event.month == month , Event.day == day, Event.year == year, Event.title == title)
            .first()
        )
        if exists:
            continue

        pages = item.get("pages",[])
        source_url = pages[0]["content_urls"]["desktop"]["page"] if pages else None


        event = Event(
            event_date = date(year, month , day) if year and year > 0 else date(1,month,day),
            day = day,
            month = month,
            year = year,
            region = Region.world,
            category = Category.other,
            title = title,
            summary = None,
            source_url=source_url,
            significance_score = 0
        )
        db.add(event)
        saved_count += 1

    db.commit()
    return saved_count

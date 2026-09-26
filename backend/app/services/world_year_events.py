import httpx
from datetime import date
from sqlalchemy.orm import Session
import re

from app.models import Event, Region, Category
from app.services.india_events import (
    HEADERS,
    MONTH_NAMES,
    DATE_LINE_PATTERN,
    clean_wikitext,
)


def fetch_year_wikitext(year: int) -> str:
    """Fetch the raw wikitext of the year '<year>' Wikipedia page (global events)."""
    url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "prop": "revisions",
        "titles": str(year),
        "rvslots": "main",
        "rvprop": "content",
        "format": "json",
    }

    response = httpx.get(
        url,
        params=params,
        headers=HEADERS,
        timeout=30.0,
    )

    response.raise_for_status()
    data = response.json()

    pages = data["query"]["pages"]
    page = next(iter(pages.values()))

    if "revisions" not in page:
        return ""

    return page["revisions"][0]["slots"]["main"]["*"]


def parse_year_events(wikitext: str) -> list[dict]:
    """Extract dated bullet-point events from the flat Events section."""
    raw_lines = []
    in_events_section = False

    for line in wikitext.splitlines():
        stripped = line.strip()

        top_level_match = re.match(r"^==([^=].*?)==$", stripped)
        if top_level_match:
            heading_text = top_level_match.group(1).strip()
            in_events_section = (heading_text.lower() == "events")
            continue

        if not in_events_section:
            continue

        if stripped.startswith("*"):
            raw_lines.append(stripped.lstrip("*").strip())

    events = []
    current_month = None
    current_day = None
    buffer_parts = []

    def flush():
        if current_month and buffer_parts:
            text = " ".join(buffer_parts).strip()
            if text:
                events.append({
                    "month": MONTH_NAMES.index(current_month) + 1,
                    "day": current_day,
                    "text": text,
                })

    for raw in raw_lines:
        cleaned = clean_wikitext(raw)  # strip [[links]], refs, bold, etc. FIRST
        match = DATE_LINE_PATTERN.match(cleaned)
        if match:
            flush()
            if match.group("month1"):
                current_month = match.group("month1")
                current_day = int(match.group("day1"))
            else:
                current_month = match.group("month2")
                current_day = int(match.group("day2"))
            remainder = cleaned[match.end():].lstrip(" \u2013\u2014-:").strip()
            buffer_parts = [remainder] if remainder else []
        else:
            if cleaned:
                buffer_parts.append(cleaned)

    flush()
    return events

def save_year_events(db:Session, year: int) -> int:
    """Fetch, parse, and save global(world) events for a given year."""
    wikitext = fetch_year_wikitext(year)
    if not wikitext:
        return 0

    parsed_events = parse_year_events(wikitext)
    saved_count = 0

    for item in parsed_events:
        month = item["month"]
        title = item["text"][:300]
        day = item["day"] if item["day"] else 1

        exists = (
            db.query(Event)
            .filter(Event.year == year, Event.month == month, Event.region == Region.world, Event.title == title)
            .first()
        )
        if exists:
            continue

        event = Event(
            event_date=date(year, month, day),
            day=day,
            month=month,
            year=year,
            region=Region.world,
            category=Category.other,
            title=title,
            summary=None,
            source_url=f"https://en.wikipedia.org/wiki/{year}",
            significance_score=0,
        )
        db.add(event)
        saved_count +=1

    db.commit()
    return saved_count
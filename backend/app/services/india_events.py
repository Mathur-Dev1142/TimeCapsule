import os
import re
import httpx
from datetime import date
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.models import Event, Region, Category

load_dotenv()

HEADERS = {
    "User-Agent": "TimeCapsule/1.0 (deepmat465@gmail.com)"
}

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

DATE_LINE_PATTERN = re.compile(
    r"^(?:(?P<day1>\d{1,2})\s+(?P<month1>" + "|".join(MONTH_NAMES) + r")"
    r"|(?P<month2>" + "|".join(MONTH_NAMES) + r")\s+(?P<day2>\d{1,2}))"
)


def fetch_india_year_wikitext(year: int) -> str:
    """Fetch the raw wikitext of the '<year> in India' Wikipedia page."""
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": f"{year} in India",
        "rvslots": "main",
        "rvprop": "content",
        "format": "json",
    }

    response = httpx.get(url, params=params, headers=HEADERS, timeout=30.0)
    response.raise_for_status()
    data = response.json()

    pages = data["query"]["pages"]
    page = next(iter(pages.values()))

    if "revisions" not in page:
        return ""

    return page["revisions"][0]["slots"]["main"]["*"]


def clean_wikitext(text: str) -> str:
    """Strip common wiki markup so text reads like plain English."""
    text = re.sub(r"\[\[(?:[^\|\]]*\|)?([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"'''?([^']+)'''?", r"\1", text)
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.DOTALL)
    text = re.sub(r"<ref[^/]*/>", "", text)
    text = re.sub(r"\{\{[^\}]*\}\}", "", text)
    return text.strip()


def parse_india_events(wikitext: str) -> list[dict]:
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
            text = clean_wikitext(" ".join(buffer_parts))
            if text:
                events.append({
                    "month": MONTH_NAMES.index(current_month) + 1,
                    "day": current_day,
                    "text": text,
                })

    for raw in raw_lines:
        match = DATE_LINE_PATTERN.match(raw)
        if match:
            flush()
            if match.group("month1"):
                current_month = match.group("month1")
                current_day = int(match.group("day1"))
            else:
                current_month = match.group("month2")
                current_day = int(match.group("day2"))
            remainder = raw[match.end():].lstrip(" \u2013\u2014-:").strip()
            buffer_parts = [remainder] if remainder else []
        else:
            cont = raw.lstrip(" \u2013\u2014-").strip()
            if cont:
                buffer_parts.append(cont)

    flush()
    return events


def save_india_events(db: Session, year: int) -> int:
    """Fetch, parse, and save India events for a given year."""
    wikitext = fetch_india_year_wikitext(year)
    if not wikitext:
        return 0

    parsed_events = parse_india_events(wikitext)
    saved_count = 0
    skipped_no_month = 0

    for item in parsed_events:
        month = item["month"]
        if month is None:
            skipped_no_month += 1
            continue

        title = item["text"][:300]
        day = item["day"] if item["day"] else 1

        exists = (
            db.query(Event)
            .filter(Event.year == year, Event.month == month, Event.region == Region.india, Event.title == title)
            .first()
        )
        if exists:
            continue

        event = Event(
            event_date=date(year, month, day),
            day=day,
            month=month,
            year=year,
            region=Region.india,
            category=Category.other,
            title=title,
            summary=None,
            source_url=f"https://en.wikipedia.org/wiki/{year}_in_India",
            significance_score=0,
        )
        db.add(event)
        saved_count += 1

    db.commit()
    if skipped_no_month:
        print(f"Note: skipped {skipped_no_month} event(s) with no identifiable month")
    return saved_count
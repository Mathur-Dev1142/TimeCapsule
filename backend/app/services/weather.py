import httpx
from datetime import date as date_type
from sqlalchemy.orm import Session

from app.models import WeatherCache

HEADERS = {
    "User-Agent": "TimeCapsule/1.0 (deepmat465@gmail.com)"
}

def fetch_historical_weather(latitude: float, longitude: float, event_date: date_type) -> dict:
    """Fetch daily weather summary for a specific date and location."""
    date_Str = event_date.isoformat()     #e.g "2007-07-05"

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude" : latitude,
        "longitude" : longitude,
        "start_date": date_Str,
        "end_date": date_Str,
        "daily" : "temperature_2m_max,temperature_2m_min,weather_code",
        "timezone" : "auto",
    }

    response = httpx.get(url, params=params, headers=HEADERS, timeout=30.0)
    response.raise_for_status()
    data = response.json()

    daily = data.get("daily", {})
    return {
        "temp_max": daily.get("temperature_2m_max", [None])[0],
        "temp_min": daily.get("temperature_2m_min", [None])[0],
        "weather_code": daily.get("weather_code", [None])[0],
    }

def save_weather(db:Session, latitude:float, longitude:float, event_date: date_type) -> dict:
    """Fetch Weather for a date/location and cache it, or return the cached copy."""
    existing= (
        db.query(WeatherCache)
        .filter(
            WeatherCache.cache_date == event_date,
            WeatherCache.latitude == latitude,
            WeatherCache.longitude == longitude
        )
        .first()
    )
    if existing:
        return{
            "temp_c": existing.temperature_c,
            "conditions": existing.conditions,
            "cached": True,
        }

    weather = fetch_historical_weather(latitude, longitude, event_date)
    avg_temp = None
    if weather["temp_max"] is not None and weather["temp_min"] is not None:
        avg_temp = round((weather["temp_max"] + weather["temp_min"])/2,1)

    conditions = describe_weather_code(weather["weather_code"])

    entry= WeatherCache(
        cache_date = event_date,
        latitude=latitude,
        longitude=longitude,
        temperature_c=avg_temp,
        conditions=conditions,
    )
    db.add(entry)
    db.commit()

    return {"temp_c": avg_temp, "conditions": conditions, "cached":False}

def describe_weather_code(code:int | None) -> str:
    """Convert Open-Meteo's numeric weather code into plain description."""
    if code is None:
        return "Unknown"

    mapping = {
        0 : "Clear Sky",
        1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        95: "Thunderstorm",
    }
    return mapping.get(code, f"code {code}")


    
"""Open-Meteo weather API wrapper."""

from copy import deepcopy
from statistics import mean
import requests
from tzlocal import get_localzone_name

def transform(data):
    """Replace daily conditions 0-3 with average hourly condition."""
    # Daily weathercode ≝ the most severe weather condition on a given day,
    # but it's questionable whether 3 is more severe than 0.
    result = deepcopy(data)
    for day, code in enumerate(data["daily"]["weathercode"]):
        if code > 3:
            continue
        avg = round(mean(data["hourly"]["weathercode"][day*24:(day + 1)*24]))
        result["daily"]["weathercode"][day] = avg
    return result

def get_forecast(latitude, longitude):
    """Request weather forecast from Open-Meteo."""
    base_url = "https://api.open-meteo.com/v1/forecast"
    payload = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,apparent_temperature,weathercode,"
                  "windspeed_10m",
        "daily": "weathercode,temperature_2m_max,temperature_2m_min,"
                 "apparent_temperature_max,apparent_temperature_min,"
                 "sunrise,sunset",
        "current_weather": "true",
        "windspeed_unit": "ms",
        "timezone": requests.utils.quote((get_localzone_name() or "auto"),
                                         safe=""),
    }
    payload_str = "&".join(f"{k}={v}" for k, v in payload.items())
    response = requests.get(base_url, params=payload_str, timeout=5)
    return transform(response.json())

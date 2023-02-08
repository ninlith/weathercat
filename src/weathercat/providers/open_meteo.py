"""Open-Meteo weather API wrapper."""

import requests
from tzlocal import get_localzone_name

def get_forecast(latitude, longitude):
    """Request weather forecast from Open-Meteo."""
    base_url = "https://api.open-meteo.com/v1/forecast"
    payload = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,weathercode,windspeed_10m",
        "daily": "weathercode,temperature_2m_max,temperature_2m_min,"
                 "apparent_temperature_max,apparent_temperature_min,"
                 "sunrise,sunset",
        "windspeed_unit": "ms",
        "timezone": requests.utils.quote((get_localzone_name() or "auto"),
                                         safe=""),
    }
    payload_str = "&".join(f"{k}={v}" for k, v in payload.items())
    response = requests.get(base_url, params=payload_str, timeout=5)
    return response.json()

# Copyright 2023 Okko Hartikainen <okko.hartikainen@yandex.com>
# This work is licensed under the GNU GPLv3. See COPYING.

"""Output."""

import logging
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo
import platformdirs
from rich.console import Console
from rich.theme import Theme
from rich.table import Table
try:
    from skyfield import api
    from skyfield import almanac
    skyfield_is_available = True  # pylint: disable=invalid-name
except ImportError:
    skyfield_is_available = False  # pylint: disable=invalid-name

logger = logging.getLogger(__package__)

custom_theme = Theme({
    "toponym": "magenta",
    "coordinates": "dim magenta",
    "sun": "yellow",
    "dim": "dim",
    "clear": "reverse bright_black",
    "partly_cloudy": "reverse dim white",
    "overcast": "reverse white",
    "fog": "reverse bright_green",
    "rain": "reverse bright_blue",
    "snow": "reverse cyan",
    "thunderstorm": "reverse bright_magenta",
    "feels_like_warmer": "bright_red",
    "feels_like_colder": "bright_cyan",
    "uv_low": "bright_green",
    "uv_moderate": "bright_yellow",
    "uv_high": "bright_red",
    "uv_very_high": "red",
    "uv_extreme": "magenta",
})

def represent_ww(code: int):  # pylint: disable=too-many-return-statements
    """Symbolize and colorize WMO Weather interpretation codes (WW)."""
    # https://open-meteo.com/en/docs#weathervariables
    if code in (0,):
        return "☀️ ", "clear"
    if code in (1, 2):
        return "🌤️ ", "partly_cloudy"
    if code in (3,):
        return "☁️ ", "overcast"
    if code in (45, 48):
        return "🌫️ ", "fog"
    if code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82):
        return "🌧️ ", "rain"
    if code in (71, 73, 75, 77, 85, 86):
        return "❄️ ", "snow"
    if code in (95, 96, 99):
        return "⚡", "thunderstorm"
    raise ValueError("Unsupported WMO Weather interpretation code: {code}")

def represent_wind(speed):
    """Symbolize wind speeds."""
    # https://www.ilmatieteenlaitos.fi/tuulet
    if speed < 3.5:
        return " "
    if speed < 7.5:
        return "⣀"
    if speed < 13.5:
        return "⣤"
    if speed < 20.5:
        return "⣶"
    return "⣿"

def represent_uvi(uvi):
    """Colorize UV index."""
    if uvi < 3:
        return f"[uv_low]{uvi}[/]"
    if uvi < 6:
        return f"[uv_moderate]{uvi}[/]"
    if uvi < 8:
        return f"[uv_high]{uvi}[/]"
    if uvi < 11:
        return f"[uv_very_high]{uvi}[/]"
    return f"[uv_extreme]{uvi}[/]"

def represent_temperature(temperature, apparent_temperature):
    """Colorize temperature based on apparent temperature."""
    # https://www.ilmatieteenlaitos.fi/saamerkkien-selitykset
    string = f"{str(round(temperature)).replace('-', '−')}"
    if apparent_temperature >= temperature + 2:
        return f"[feels_like_warmer]{string}[/]"
    if apparent_temperature <= temperature - 5:
        return f"[feels_like_colder]{string}[/]"
    return string

def fabricate_moon_function():
    """Create a lunar phase representation function."""
    if skyfield_is_available:
        timescale = api.load.timescale()
        directory = platformdirs.user_data_path("weathercat")
        filename = "de421.bsp"
        file = directory / filename
        try:
            eph = api.load_file(file)
            logger.debug(f"Loaded {file}")
        except FileNotFoundError:
            load = api.Loader(directory, verbose=True)
            url = load.build_url(filename)
            logger.info(f"Downloading ephemeris DE421 from {url}")
            eph = load(filename)
        def moon(date, timezone):
            """Indicate whether the full moon occurs during a given date."""
            dt0 = datetime.fromisoformat(date).replace(
                tzinfo=ZoneInfo(timezone))
            dt1 = datetime.combine(dt0, dt0.time().max).replace(
                tzinfo=ZoneInfo(timezone))
            start_time = timescale.from_datetime(dt0)
            end_time = timescale.from_datetime(dt1)
            _times, phases = almanac.find_discrete(start_time,
                                                   end_time,
                                                   almanac.moon_phases(eph))
            del _times  # unused
            if "Full Moon" in [almanac.MOON_PHASES[phase] for phase in phases]:
                return "🌕"
            return ""
        return moon
    return lambda *args: ""

def output(forecast, toponym):
    """Output a forecast."""
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements
    superscript = {ord(k): v for k, v in zip("+-−0123456789", "⁺⁻⁻⁰¹²³⁴⁵⁶⁷⁸⁹")}
    subscript = {ord(k): v for k, v in zip("+-−0123456789", "₊₋₋₀₁₂₃₄₅₆₇₈₉")}

    forecast_table = Table.grid(padding=(0, 1))
    forecast_table.add_column("hourly", no_wrap=True)
    forecast_table.add_column("day")
    forecast_table.add_column("symbol")
    forecast_table.add_column("min_temperature", no_wrap=True, justify="right")
    forecast_table.add_column("max_temperature", no_wrap=True, justify="right")
    forecast_table.add_column("uvi", no_wrap=True)
    forecast_table.add_column("moon")
    hour = datetime.now().hour
    markers = defaultdict(lambda: "00    06    12    18    24"
                                  .translate(subscript))
    markers[0] = markers[0][:hour] + "🐈" + markers[0][hour + 2:]
    # pylint: disable=unnecessary-lambda-assignment
    condition = lambda i: represent_ww(forecast["hourly"]["weathercode"][i])[1]
    wind = lambda i: represent_wind(forecast["hourly"]["windspeed_10m"][i])
    # pylint: enable=unnecessary-lambda-assignment
    moon = fabricate_moon_function()
    for day in range(7):
        condition_bar = "".join(["[" + condition(i) + "]" + wind(i) + "[/]"
                                 for i in [day*24 + h for h in range(24)]])
        weekday = datetime.fromisoformat(
            forecast["daily"]["time"][day]).strftime("%a")
        weather_symbol = represent_ww(forecast["daily"]["weathercode"][day])[0]
        min_temperature = represent_temperature(
            forecast["daily"]["temperature_2m_min"][day],
            forecast["daily"]["apparent_temperature_min"][day])
        max_temperature = represent_temperature(
            forecast["daily"]["temperature_2m_max"][day],
            forecast["daily"]["apparent_temperature_max"][day])
        uvi = represent_uvi(
            round(forecast["daily"]["uv_index_max"][day])
            ).translate(subscript)
        moon_symbol = moon(forecast["daily"]["time"][day],
                           forecast["timezone"])
        temperatures = "  ".join(
            f'{round(forecast["hourly"]["temperature_2m"][i]):>3}' for i in
            [day*24 + h for h in range(2, 23, 5)]).translate(superscript)
        forecast_table.add_row(
            f" [dim]{markers[day]}[/]")
        forecast_table.add_row(
            f"  {condition_bar}",
            f"[dim]{weekday}[/] ",
            f"{weather_symbol}",
            f" {min_temperature} [dim]/[/]",
            f"{max_temperature} [dim]°C[/]",
            f" [dim]ᵁⱽ[/]{uvi}",
            f" {moon_symbol}")
        forecast_table.add_row(
            f"  {temperatures}")

    sunrise = forecast["daily"]["sunrise"][0].split("T")[1]
    sunset = forecast["daily"]["sunset"][0].split("T")[1]
    uvi_clear_sky = represent_uvi(round(
        forecast["daily"]["uv_index_clear_sky_max"][0])).translate(superscript)
    current_date, current_time = forecast["current_weather"]["time"].split("T")
    current_weather = represent_ww(
        forecast["current_weather"]["weathercode"])[0]
    current_temperature = represent_temperature(
        forecast["current_weather"]["temperature"],
        forecast["hourly"]["apparent_temperature"][
            forecast["hourly"]["time"].index(
                forecast["current_weather"]["time"][:-3] + ":00")])
    details_table = Table.grid(expand=True)
    details_table.add_column(justify="right")
    toponym = toponym.rsplit(",", 1)
    details_table.add_row(f"[toponym]{toponym[0]}[/]")
    if len(toponym) > 1:
        details_table.add_row(f"[toponym][dim]{toponym[1]}[/][/]")
    details_table.add_row()
    details_table.add_row(f"[sun]☉  {sunrise}–{sunset}[/]")
    details_table.add_row(
        f"[sun][dim]{current_date}[/][/]".translate(superscript))
    details_table.add_row()
    details_table.add_row(f"[dim]{current_time}[/]  {current_weather}  "
                          f"{current_temperature} [dim]°C[/]")

    console = Console(theme=custom_theme)
    if console.size.width < 80:
        outer_table = Table.grid(padding=(1, 0), expand=True)
        outer_table.add_column()
        outer_table.add_row(details_table)
        outer_table.add_row(forecast_table)
    else:
        outer_table = Table.grid(padding=(0, 2), expand=True)
        outer_table.add_column(no_wrap=True)
        outer_table.add_column()
        outer_table.add_row(forecast_table, details_table)
    console.print(outer_table)

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
    "sun": "yellow",
    "dim": "dim",
    "clear": "reverse bright_black",
    "partly_cloudy": "reverse dim white",
    "overcast": "reverse white",
    "fog": "reverse bright_magenta",
    "rain": "reverse bright_blue",
    "snow": "reverse cyan",
    "thunderstorm": "reverse bright_yellow",
    "feels_like_warmer": "bright_red",
    "feels_like_colder": "bright_cyan",
})

def represent_ww(code: int):  # pylint: disable=too-many-return-statements
    """Symbolize and colorize WMO Weather interpretation codes (WW)."""
    # https://open-meteo.com/en/docs#weathervariables
    if code in (0,):
        return "☀️", "clear"
    if code in (1, 2):
        return "🌤️", "partly_cloudy"
    if code in (3,):
        return "☁️", "overcast"
    if code in (45, 48):
        return "🌫️", "fog"
    if code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82):
        return "🌧️", "rain"
    if code in (71, 73, 75, 77, 85, 86):
        return "❄️", "snow"
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

def represent_temperature(t_min, t_max, apparent_min, apparent_max):
    """Colorize temperature based on apparent temperature."""
    # https://www.ilmatieteenlaitos.fi/saamerkkien-selitykset
    temperature = (t_min + t_max)/2
    apparent_temperature = (apparent_min + apparent_max)/2
    string = f"{str(round(temperature)).replace('-', '−')} °C"
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
    superscript = {ord(k): v for k, v in zip("+-−0123456789", "⁺⁻⁻⁰¹²³⁴⁵⁶⁷⁸⁹")}
    subscript = {ord(k): v for k, v in zip("+-−0123456789", "₊₋₋₀₁₂₃₄₅₆₇₈₉")}

    table = Table.grid(padding=(0, 1))
    table.add_column("hourly", no_wrap=True)
    table.add_column("day", no_wrap=True)
    table.add_column("symbol", no_wrap=True)
    table.add_column("temperature", no_wrap=True, justify="right")
    table.add_column("moon", no_wrap=True)
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
        table.add_row(" [dim]" + markers[day] + "[/]")
        table.add_row(
            "  " + "".join(["[" + condition(i) + "]" + wind(i) + "[/]"
                            for i in [day*24 + h for h in range(24)]]),
            datetime.fromisoformat(forecast["daily"]["time"][day])
                                   .strftime("[dim]%a[/] "),
            represent_ww(forecast["daily"]["weathercode"][day])[0],
            "  " + represent_temperature(
                forecast["daily"]["temperature_2m_min"][day],
                forecast["daily"]["temperature_2m_max"][day],
                forecast["daily"]["apparent_temperature_min"][day],
                forecast["daily"]["apparent_temperature_max"][day]),
            " " + moon(forecast["daily"]["time"][day], forecast["timezone"]))
        table.add_row("  " + "  ".join(
            f'{round(forecast["hourly"]["temperature_2m"][i]):>3}' for i in
            [day*24 + h for h in range(2, 23, 5)]).translate(superscript))

    sunrise = forecast["daily"]["sunrise"][0].split("T")[1]
    sunset = forecast["daily"]["sunset"][0].split("T")[1]
    outer_table = Table.grid(padding=(0, 2), expand=True)
    outer_table.add_column(no_wrap=True)
    outer_table.add_column(justify="right")
    outer_table.add_row(
        table,
        f"[toponym]{toponym}[/]\n\n[sun]☉  {sunrise}–{sunset}[/]")
    console = Console(theme=custom_theme)
    console.print(outer_table)

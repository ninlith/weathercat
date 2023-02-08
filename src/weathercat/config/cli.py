# Copyright 2023 Okko Hartikainen <okko.hartikainen@yandex.com>
# This work is licensed under the GNU GPLv3. See COPYING.

"""Command-line interface."""

import argparse
import logging
import sys
from importlib.metadata import metadata
from rich import box
from rich.console import Console
from rich.table import Table
from weathercat.output import custom_theme

def print_epilog():
    """Print additional help."""
    conditions = Table.grid(padding=(0, 1))
    conditions.add_column()
    conditions.add_column()
    conditions.add_row("[clear] [/] ", "clear")
    conditions.add_row("[partly_cloudy] [/] ", "partly cloudy")
    conditions.add_row("[overcast] [/] ", "overcast")
    conditions.add_row("[fog] [/] ", "fog")
    conditions.add_row("[rain] [/] ", "rain")
    conditions.add_row("[snow] [/] ", "snow")
    conditions.add_row("[thunderstorm] [/] ", "thunderstorm")

    wind_speeds = Table.grid(padding=(0, 1))
    wind_speeds.add_column(no_wrap=True)
    wind_speeds.add_column(no_wrap=True, justify="right")
    wind_speeds.add_column()
    wind_speeds.add_row("[reverse] [/] ", "0–3 m/s", "(calm or light wind)")
    wind_speeds.add_row("[reverse]⣀[/] ", "4–7 m/s", "(moderate wind)")
    wind_speeds.add_row("[reverse]⣤[/] ", "8–13 m/s", "(fresh breeze)")
    wind_speeds.add_row("[reverse]⣶[/] ", "14–20 m/s", "(strong wind)")
    wind_speeds.add_row("[reverse]⣿[/] ", "≥ 21 m/s", "(storm)")

    apparent_temperatures = Table.grid(padding=(0, 1))
    apparent_temperatures.add_column(no_wrap=True)
    apparent_temperatures.add_column()
    apparent_temperatures.add_row("[feels_like_warmer]T °C[/] ",
                                  "at least 2 degrees warmer than T")
    apparent_temperatures.add_row("[feels_like_colder]T °C[/] ",
                                  "at least 5 degrees colder than T")

    outer_table = Table(box=box.ROUNDED, border_style="dim")
    outer_table.add_column("Conditions")
    outer_table.add_column("Wind speeds")
    outer_table.add_column("Apparent temperatures")
    outer_table.add_row(conditions, wind_speeds, apparent_temperatures)
    console = Console(theme=custom_theme)
    console.print(outer_table)

def parse_arguments(argv=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=metadata("weathercat")["Summary"],
        add_help=False,
        )
    parser.add_argument(
        "-h", "--help",
        action="store_true",
        help="show this help message and exit",
        )
    parser.add_argument(
        "-d", "--debug",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
        help="enable DEBUG logging level",
        )
    parser.add_argument(
        "-a", "--autolocate",
        action="store_true",
        help="force location autodetection",
        )
    parser.add_argument(
        "location",
        metavar="LOCATION",
        nargs="*",
        help="free-form query or coordinates (geo URI or latitude, longitude)",
        )
    args, unknown_args = parser.parse_known_args(argv)
    if args.help:
        parser.print_help()
        print()
        print_epilog()
        sys.exit()
    if unknown_args:
        args.location = unknown_args + args.location
    return args

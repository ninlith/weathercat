# Copyright 2023 Okko Hartikainen <okko.hartikainen@yandex.com>
# This work is licensed under the GNU GPLv3. See COPYING.

"""Command-line interface."""

import argparse
import logging
from importlib.metadata import metadata

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=metadata("weathercat")["Summary"],
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
        "location",
        metavar="LOCATION",
        nargs="?",
        help="textual description or latitude, longitude",
        )
    return parser.parse_args()

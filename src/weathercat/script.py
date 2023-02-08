# Copyright 2023 Okko Hartikainen <okko.hartikainen@yandex.com>
# This work is licensed under the GNU GPLv3. See COPYING.

"""Terminal weather."""

import locale
import logging
import sys
from weathercat import __version__
from weathercat.config import parse_arguments, parse_config_file, setup_logging
from weathercat.geolocation import geolocate, georesolve
from weathercat.providers.open_meteo import get_forecast
from weathercat.output import output

logger = logging.getLogger(__name__)

def main():
    """Execute."""
    args = parse_arguments()
    setup_logging(args.loglevel)
    logger.debug(f"{__version__ = }")
    conf = parse_config_file()
    locale.setlocale(locale.LC_ALL, conf.get("locale", ""))

    if args.location:
        try:
            toponym, ϕ, λ = georesolve(" ".join(args.location))
        except LookupError as exc:
            print(exc)
            sys.exit(1)
    elif "default_location" in conf:
        toponym, ϕ, λ = [conf["default_location"][x]
                         for x in ["name", "latitude", "longitude"]]
    else:
        toponym, ϕ, λ = georesolve(" ".join(str(x) for x in geolocate()))
    logger.debug(f"{toponym = }, {ϕ = }, {λ = }")

    forecast = get_forecast(ϕ, λ)
    output(forecast, toponym)

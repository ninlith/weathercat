# Copyright 2023 Okko Hartikainen <okko.hartikainen@yandex.com>
# This work is licensed under the GNU GPLv3. See COPYING.

"""Logging configuration."""

import logging
import logging.config

def setup_logging(loglevel):
    """Set up logging configuration."""
    logging.config.dictConfig(dict(
        version=1,
        disable_existing_loggers=False,
        formatters={
            "f": {
                "class": "colorlog.ColoredFormatter",
                "format": "%(fg_thin_white)s%(asctime)s%(reset)s "
                          "%(log_color)s%(levelname)-3.3s%(reset)s "
                          "%(fg_thin_cyan)s[%(name)s]%(reset)s %(message)s",
                "datefmt": "%F %T"}},
        handlers={
            "h": {
                "class": "logging.StreamHandler",
                "formatter": "f",
                "level": loglevel}},
        root={
            "handlers": ["h"],
            "level": loglevel},
        ))

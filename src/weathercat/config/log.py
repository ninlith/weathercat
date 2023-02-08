# Copyright 2023 Okko Hartikainen <okko.hartikainen@yandex.com>
# This work is licensed under the GNU GPLv3. See COPYING.

"""Logging configuration."""

import logging
from rich.console import Console
from rich.logging import RichHandler

def setup_logging(loglevel):
    """Set up logging configuration."""
    logging.basicConfig(level=loglevel,
                        format="%(message)s",
                        datefmt="[%T]",
                        handlers=[RichHandler(console=Console(stderr=True))])

    # https://stackoverflow.com/a/66416102
    old_factory = logging.getLogRecordFactory()
    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)  # get the unmodified record
        record.lineno = None
        record.pathname = record.name
        return record
    logging.setLogRecordFactory(record_factory)

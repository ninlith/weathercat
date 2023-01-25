# Copyright 2023 Okko Hartikainen <okko.hartikainen@yandex.com>
# This work is licensed under the GNU GPLv3. See COPYING.

"""Terminal weather."""

import logging
from weathercat import __version__
from weathercat.config.log import setup_logging

logger = logging.getLogger(__name__)

def main():
    """Execute."""
    setup_logging(logging.DEBUG)
    logger.debug(f"{__version__ = }")

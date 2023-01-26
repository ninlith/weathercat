# Copyright 2023 Okko Hartikainen <okko.hartikainen@yandex.com>
# This work is licensed under the GNU GPLv3. See COPYING.

"""Configuration file handling."""

import logging
import platformdirs
import tomli

logger = logging.getLogger(__name__)

def parse_config_file() -> dict:
    """Read or create a configuration file."""
    config_directory = platformdirs.user_config_path("weathercat")
    config_file = config_directory / "weathercat.conf"
    if not config_file.is_file():
        logger.debug(f"Creating '{config_file}'")
        try:
            config_directory.mkdir(parents=True, exist_ok=True)
            config_file.write_text(
                '# default_location = "geo:61.000689,24.479063"\n'
                '# locale = "fi_FI.UTF-8"\n')
        except OSError as error:  # handle read-only file system etc.
            logger.error(error)
        return {}
    logger.debug(f"Reading '{config_file}'")
    with open(config_file, mode="rb") as file_object:
        return tomli.load(file_object)

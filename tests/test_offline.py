"""Test connection failures."""

import logging
import sys
from importlib import reload
from unittest.mock import patch
import pytest
from weathercat.geolocation import georesolve, geolocate

logger = logging.getLogger(__name__)

def test_georesolve(caplog, no_network):  # pylint: disable=unused-argument
    """Test georesolve."""
    assert georesolve("61, 24") == (None, 61, 24)
    with pytest.raises(ConnectionError) as exc_info:
        georesolve("Hämeenlinna")
    logger.exception(exc_info)

def test_geolocate(caplog, no_network):  # pylint: disable=unused-argument
    """Test geocoder in geolocate."""
    with (patch.dict(sys.modules, {"gi": None}),  # no-gi
          pytest.raises(ConnectionError) as exc_info):
        reload(sys.modules["weathercat.geolocation.geolocation"])
        geolocate()
    logger.exception(exc_info)

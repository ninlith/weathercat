"""Test connection failures."""

import logging
import pytest
from weathercat.geolocation import georesolve, geolocate

logger = logging.getLogger(__name__)

def test_georesolve(caplog, no_network):  #pylint: disable=W0613
    """Test georesolve."""
    assert georesolve("61, 24") == (None, 61, 24)
    with pytest.raises(ConnectionError) as exc_info:
        georesolve("Hämeenlinna")
    logger.exception(exc_info)

def test_geolocate(caplog, no_network):  #pylint: disable=W0613
    """Test geolocate."""
    try:
        import gi
    except ImportError:
        with pytest.raises(ConnectionError) as exc_info:
            geolocate()
        logger.exception(exc_info)

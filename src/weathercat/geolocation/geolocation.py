"""Geolocation."""

from __future__ import annotations
import locale
import logging
import re
from multiprocessing import Process, Queue
import geocoder
import geopy
try:
    import gi
    gi.require_version("Geoclue", "2.0")
    from gi.repository import Geoclue
except ImportError:
    gi = None

logger = logging.getLogger(__name__)

def georesolve(location: str) -> tuple[str | None, float, float]:
    """Resolve description or coordinates to toponym and coordinates."""
    geolocator = geopy.geocoders.Nominatim(user_agent="weathercat")
    language = (locale.getlocale()[0] or "en").replace("_", "-")
    pattern = r"(?:geo:)?-?([0-9]+\.?[0-9]*)[ ,]+-?([0-9]+\.?[0-9]*).*"
    if match_coordinates := re.match(pattern, location):
        try:
            response = geolocator.reverse(match_coordinates.string,
                                          language=language,
                                          addressdetails=True)
        except geopy.exc.GeocoderServiceError:
            logger.warning("Connection to Nominatim failed")
            return None, *map(float, match_coordinates.groups())
    else:
        try:
            response = geolocator.geocode(location,
                                          language=language,
                                          addressdetails=True)
        except geopy.exc.GeocoderServiceError as exc:
            raise ConnectionError("Connection to Nominatim failed") from exc
    if not response:
        raise LookupError(f"Unknown location: {location}")
    logger.debug(f"{response.raw = }")
    if any(x in response.raw["address"] for x in ("city", "town", "village")):
        toponym = ", ".join(response.raw["address"][x]
                            for x in ("city", "town", "village", "country")
                            if x in response.raw["address"])
    else:
        toponym = response.address
    return toponym, response.latitude, response.longitude

def geolocate() -> tuple[float, float]:
    """Autodetect geolocation."""
    def geoclue_locate(queue):
        clue = Geoclue.Simple.new_sync("something",
                                       Geoclue.AccuracyLevel.NEIGHBORHOOD,
                                       None)
        location = clue.get_location()
        queue.put((location.get_property("latitude"),
                   location.get_property("longitude")))
    if gi:
        logger.debug("Using Geoclue")
        queue = Queue()
        process = Process(target=geoclue_locate, args=(queue,))
        process.start()
        process.join(timeout=2)
        process.terminate()
        if process.exitcode is None:
            logger.warning("Geoclue timeout")
        else:
            return queue.get()

    if coordinates := geocoder.ip("").latlng:
        return coordinates
    raise ConnectionError("Connection to an IP geolocation service failed")

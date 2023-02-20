"""Test output."""

import ast
import pkgutil
from weathercat.output import output, represent_temperature
from weathercat.providers.open_meteo import transform

def print_saved_forecast():
    """Test output with offline data."""
    data = pkgutil.get_data(__name__, "forecast.txt")
    forecast = ast.literal_eval(data.decode("utf8"))
    forecast = transform(forecast)
    output(forecast,
           "Hölmölä, 24, Saarelantie, Evo, Hämeenlinna, Hämeenlinnan "
           "seutukunta, Kanta-Häme, Etelä-Suomen aluehallintovirasto, "
           "Manner-Suomi, 16970, Suomi")

def test_temperature():
    """Test temperature representation."""
    assert "feels_like_warmer" in represent_temperature(0, 0, 2, 2)
    assert "feels_like_warmer" not in represent_temperature(0, 0, 1, 1)
    assert "feels_like_colder" in represent_temperature(0, 0, -5, -5)
    assert "feels_like_colder" not in represent_temperature(0, 0, -4, -4)

"""Configurations."""

import socket
import pytest
from test_output import print_saved_forecast

@pytest.fixture
def no_network(monkeypatch):
    """Raise get address info error."""
    def socket_mock(*args, **kwargs):
        raise socket.gaierror("mocked")
    monkeypatch.setattr("socket.socket", socket_mock)

def pytest_sessionstart(session):  # pylint: disable=unused-argument
    """Run code before collection and run test loop."""
    print_saved_forecast()

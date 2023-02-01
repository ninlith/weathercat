"""Configurations."""

import socket
import pytest

@pytest.fixture
def no_network(monkeypatch):
    """Raise get address info error."""
    def socket_mock(*args, **kwargs):
        raise socket.gaierror("mocked")
    monkeypatch.setattr("socket.socket", socket_mock)

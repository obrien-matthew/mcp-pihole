"""Tests for the Pi-hole client."""

from pihole_mcp.client import Pi-holeClient


class TestClient:
    def test_ping(self):
        client = Pi-holeClient()
        assert client.ping() == "pong"

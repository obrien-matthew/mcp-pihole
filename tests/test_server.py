"""Tests for MCP server setup."""

from pihole_mcp.server import mcp


class TestServerCreation:
    def test_server_exists(self):
        assert mcp is not None

    def test_server_name(self):
        assert mcp.name == "mcp-pihole"

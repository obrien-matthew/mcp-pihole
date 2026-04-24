"""Tests for MCP server setup and tool registration."""

from pihole_mcp.server import mcp

EXPECTED_TOOLS = [
    "get_status",
    "get_top_domains",
    "get_top_clients",
    "get_queries",
    "get_version",
    "get_lists",
    "add_list",
    "remove_list",
    "update_list",
    "update_gravity",
    "get_domains",
    "add_domain",
    "remove_domain",
    "search_domains",
    "get_blocking_status",
    "set_blocking",
    "get_dhcp_leases",
    "restart_dns",
]


class TestServerCreation:
    def test_server_exists(self):
        assert mcp is not None

    def test_server_name(self):
        assert mcp.name == "mcp-pihole"


class TestToolRegistration:
    def test_all_tools_registered(self):
        tool_names = list(mcp._tool_manager._tools.keys())
        for name in EXPECTED_TOOLS:
            assert name in tool_names, f"Tool '{name}' not registered"

    def test_no_unexpected_tools(self):
        tool_names = list(mcp._tool_manager._tools.keys())
        for name in tool_names:
            assert name in EXPECTED_TOOLS, f"Unexpected tool '{name}'"

    def test_tool_count(self):
        assert len(mcp._tool_manager._tools) == len(EXPECTED_TOOLS)

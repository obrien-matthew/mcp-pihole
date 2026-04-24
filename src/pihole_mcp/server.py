"""MCP server with Pi-hole tools for DNS management."""

import json

from mcp.server.fastmcp import FastMCP

from .client import PiholeClient, PiholeError
from .formatting import (
    format_blocking_status,
    format_domain_entry,
    format_lease,
    format_list_entry,
    format_queries,
    format_search_results,
    format_summary,
    format_top_clients,
    format_top_domains,
    format_version,
)
from .validation import (
    validate_count,
    validate_domain_kind,
    validate_domain_type,
    validate_url,
)

mcp = FastMCP("mcp-pihole")

_client: PiholeClient | None = None


def _get_client() -> PiholeClient:
    global _client
    if _client is None:
        _client = PiholeClient()
    return _client


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------


@mcp.tool()
def get_status() -> str:
    """Get Pi-hole status summary.

    Returns blocking status, total queries today, blocked count,
    percentage blocked, domains on blocklist, clients seen,
    unique domains, cached and forwarded query counts.
    """
    try:
        client = _get_client()
        summary = client.get_summary()
        blocking = client.get_blocking()
        return json.dumps(format_summary(summary, blocking), indent=2)
    except (PiholeError, ValueError) as e:
        return f"Error: {e}"


@mcp.tool()
def get_top_domains(count: int = 10, blocked: bool = False) -> str:
    """Get top queried domains.

    count: number of domains to return (max 100).
    blocked: if True, returns top blocked domains instead of top permitted.
    """
    try:
        count = validate_count(count)
        result = _get_client().get_top_domains(count, blocked)
        return json.dumps(format_top_domains(result), indent=2)
    except (PiholeError, ValueError) as e:
        return f"Error: {e}"


@mcp.tool()
def get_top_clients(count: int = 10, blocked: bool = False) -> str:
    """Get top DNS clients by query count.

    count: number of clients to return (max 100).
    blocked: if True, returns clients with most blocked queries.
    """
    try:
        count = validate_count(count)
        result = _get_client().get_top_clients(count, blocked)
        return json.dumps(format_top_clients(result), indent=2)
    except (PiholeError, ValueError) as e:
        return f"Error: {e}"


@mcp.tool()
def get_queries(length: int = 100, cursor: int | None = None) -> str:
    """Get recent DNS queries.

    length: number of queries to return (max 100).
    cursor: database ID for cursor-based pagination. Pass the cursor
            value from a previous response to get the next page.
    """
    try:
        length = validate_count(length)
        result = _get_client().get_queries(length, cursor)
        return json.dumps(format_queries(result), indent=2)
    except (PiholeError, ValueError) as e:
        return f"Error: {e}"


@mcp.tool()
def get_version() -> str:
    """Get Pi-hole FTL version information."""
    try:
        result = _get_client().get_version()
        return json.dumps(format_version(result), indent=2)
    except (PiholeError, ValueError) as e:
        return f"Error: {e}"


# ---------------------------------------------------------------------------
# Blocklist management
# ---------------------------------------------------------------------------


@mcp.tool()
def get_lists() -> str:
    """Get all configured blocklists.

    Returns each list's URL, enabled/disabled status, comment, and groups.
    """
    try:
        result = _get_client().get_lists()
        lists = result.get("lists", [])
        return json.dumps([format_list_entry(entry) for entry in lists], indent=2)
    except (PiholeError, ValueError) as e:
        return f"Error: {e}"


@mcp.tool()
def add_list(address: str, comment: str = "", enabled: bool = True) -> str:
    """Add a blocklist by URL.

    address: URL of the blocklist (e.g., https://example.com/hosts.txt).
    comment: optional description.
    enabled: whether the list is active (default True).

    After adding, run update_gravity to apply changes.
    """
    try:
        address = validate_url(address)
        result = _get_client().add_list(address, comment, enabled)
        lists = result.get("lists", [])
        entry = lists[0] if lists else result
        return json.dumps(format_list_entry(entry), indent=2)
    except (PiholeError, ValueError) as e:
        return f"Error: {e}"


@mcp.tool()
def remove_list(address: str) -> str:
    """Remove a blocklist by URL.

    address: exact URL of the blocklist to remove.
    After removing, run update_gravity to apply changes.
    """
    try:
        address = validate_url(address)
        _get_client().remove_list(address)
        return f"Removed blocklist: {address}"
    except (PiholeError, ValueError) as e:
        return f"Error: {e}"


@mcp.tool()
def update_list(
    address: str,
    enabled: bool | None = None,
    comment: str | None = None,
) -> str:
    """Update a blocklist's enabled status or comment.

    address: exact URL of the blocklist to update.
    enabled: set True to enable, False to disable.
    comment: update the list's description.

    Only provided fields are changed. After changes, run update_gravity.
    """
    try:
        address = validate_url(address)
        result = _get_client().update_list(address, enabled, comment)
        lists = result.get("lists", [])
        entry = lists[0] if lists else result
        return json.dumps(format_list_entry(entry), indent=2)
    except (PiholeError, ValueError) as e:
        return f"Error: {e}"


@mcp.tool()
def update_gravity() -> str:
    """Rebuild the gravity database.

    Required after adding, removing, or modifying blocklists for changes
    to take effect. Runs asynchronously on the Pi-hole server.
    """
    try:
        result = _get_client().update_gravity()
        if result:
            return "Gravity update completed."
        return "Gravity update started."
    except (PiholeError, ValueError) as e:
        return f"Error: {e}"


# ---------------------------------------------------------------------------
# Domain management
# ---------------------------------------------------------------------------


@mcp.tool()
def get_domains(type: str = "deny", kind: str = "exact") -> str:
    """Get configured domain entries.

    type: "allow" (whitelist) or "deny" (blacklist).
    kind: "exact" (exact match) or "regex" (regular expression).
    """
    try:
        type = validate_domain_type(type)
        kind = validate_domain_kind(kind)
        result = _get_client().get_domains(type, kind)
        domains = result.get("domains", [])
        return json.dumps([format_domain_entry(d) for d in domains], indent=2)
    except (PiholeError, ValueError) as e:
        return f"Error: {e}"


@mcp.tool()
def add_domain(
    domain: str,
    type: str = "deny",
    kind: str = "exact",
    comment: str = "",
) -> str:
    """Add a domain to the allow or deny list.

    domain: the domain or regex pattern to add.
    type: "allow" (whitelist) or "deny" (blacklist).
    kind: "exact" (exact domain match) or "regex" (regular expression).
    comment: optional description.
    """
    try:
        type = validate_domain_type(type)
        kind = validate_domain_kind(kind)
        result = _get_client().add_domain(domain, type, kind, comment)
        domains = result.get("domains", [])
        entry = domains[0] if domains else result
        return json.dumps(format_domain_entry(entry), indent=2)
    except (PiholeError, ValueError) as e:
        return f"Error: {e}"


@mcp.tool()
def remove_domain(domain: str, type: str = "deny", kind: str = "exact") -> str:
    """Remove a domain from the allow or deny list.

    domain: the exact domain or regex pattern to remove.
    type: "allow" or "deny".
    kind: "exact" or "regex".
    """
    try:
        type = validate_domain_type(type)
        kind = validate_domain_kind(kind)
        _get_client().remove_domain(domain, type, kind)
        return f"Removed {type}/{kind} domain: {domain}"
    except (PiholeError, ValueError) as e:
        return f"Error: {e}"


@mcp.tool()
def search_domains(domain: str) -> str:
    """Check if a domain is blocked and by which list.

    Searches gravity, antigravity, exact deny/allow, and regex deny/allow
    lists. Useful for troubleshooting why a domain is blocked or allowed.
    """
    try:
        result = _get_client().search_domains(domain)
        return json.dumps(format_search_results(result), indent=2)
    except (PiholeError, ValueError) as e:
        return f"Error: {e}"


# ---------------------------------------------------------------------------
# DNS control + DHCP
# ---------------------------------------------------------------------------


@mcp.tool()
def get_blocking_status() -> str:
    """Get current DNS blocking status.

    Returns whether blocking is enabled/disabled and any active timer.
    """
    try:
        result = _get_client().get_blocking()
        return json.dumps(format_blocking_status(result), indent=2)
    except (PiholeError, ValueError) as e:
        return f"Error: {e}"


@mcp.tool()
def set_blocking(enabled: bool, timer: int | None = None) -> str:
    """Enable or disable DNS blocking.

    enabled: True to enable, False to disable.
    timer: optional seconds before blocking auto-reverts.
           Example: set_blocking(False, 300) disables for 5 minutes.
    """
    try:
        result = _get_client().set_blocking(enabled, timer)
        return json.dumps(format_blocking_status(result), indent=2)
    except (PiholeError, ValueError) as e:
        return f"Error: {e}"


@mcp.tool()
def get_dhcp_leases() -> str:
    """Get current DHCP leases.

    Returns active leases with IP, MAC address, hostname, and expiry time.
    """
    try:
        result = _get_client().get_dhcp_leases()
        leases = result.get("leases", [])
        return json.dumps([format_lease(le) for le in leases], indent=2)
    except (PiholeError, ValueError) as e:
        return f"Error: {e}"


@mcp.tool()
def restart_dns() -> str:
    """Restart the Pi-hole DNS resolver.

    Use after configuration changes that require a DNS restart.
    """
    try:
        _get_client().restart_dns()
        return "DNS resolver restarted."
    except (PiholeError, ValueError) as e:
        return f"Error: {e}"

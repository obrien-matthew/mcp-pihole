"""MCP server with Pi-hole tools for DNS management.

Tool return-type conventions:
- Data tools return real `dict` or `list[dict]` so FastMCP serializes them as
  proper structured content (no json.dumps wrapping).
- Action/status tools return human-readable `str` confirmations.
- Errors are raised as exceptions; FastMCP translates them into MCP error
  responses with `isError=true`.
"""

from importlib.metadata import PackageNotFoundError, version

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


@mcp.tool()
def get_server_version() -> str:
    """Return the installed version of the mcp-pihole server."""
    try:
        return version("mcp-pihole")
    except PackageNotFoundError:
        return "unknown"


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
def get_status() -> dict:
    """Get Pi-hole status summary.

    Returns blocking status, total queries today, blocked count,
    percentage blocked, domains on blocklist, clients seen,
    unique domains, cached and forwarded query counts.
    """
    client = _get_client()
    summary = client.get_summary()
    blocking = client.get_blocking()
    return format_summary(summary, blocking)


@mcp.tool()
def get_top_domains(count: int = 10, blocked: bool = False) -> dict:
    """Get top queried domains.

    count: number of domains to return (max 100).
    blocked: if True, returns top blocked domains instead of top permitted.
    """
    count = validate_count(count)
    result = _get_client().get_top_domains(count, blocked)
    return format_top_domains(result)


@mcp.tool()
def get_top_clients(count: int = 10, blocked: bool = False) -> dict:
    """Get top DNS clients by query count.

    count: number of clients to return (max 100).
    blocked: if True, returns clients with most blocked queries.
    """
    count = validate_count(count)
    result = _get_client().get_top_clients(count, blocked)
    return format_top_clients(result)


@mcp.tool()
def get_queries(length: int = 100, cursor: int | None = None) -> dict:
    """Get recent DNS queries.

    length: number of queries to return (max 100).
    cursor: database ID for cursor-based pagination. Pass the cursor
            value from a previous response to get the next page.
    """
    length = validate_count(length)
    result = _get_client().get_queries(length, cursor)
    return format_queries(result)


@mcp.tool()
def get_version() -> dict:
    """Get Pi-hole FTL version information."""
    return format_version(_get_client().get_version())


# ---------------------------------------------------------------------------
# Blocklist management
# ---------------------------------------------------------------------------


@mcp.tool()
def get_lists() -> list[dict]:
    """Get all configured blocklists.

    Returns each list's URL, enabled/disabled status, comment, and groups.
    """
    result = _get_client().get_lists()
    lists = result.get("lists", [])
    return [format_list_entry(entry) for entry in lists]


@mcp.tool()
def add_list(address: str, comment: str = "", enabled: bool = True) -> dict:
    """Add a blocklist by URL.

    address: URL of the blocklist (e.g., https://example.com/hosts.txt).
    comment: optional description.
    enabled: whether the list is active (default True).

    After adding, run update_gravity to apply changes.
    """
    address = validate_url(address)
    result = _get_client().add_list(address, comment, enabled)
    lists = result.get("lists", [])
    entry = lists[0] if lists else result
    return format_list_entry(entry)


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
) -> dict:
    """Update a blocklist's enabled status or comment.

    address: exact URL of the blocklist to update.
    enabled: set True to enable, False to disable.
    comment: update the list's description.

    Only provided fields are changed. After changes, run update_gravity.
    """
    address = validate_url(address)
    result = _get_client().update_list(address, enabled, comment)
    lists = result.get("lists", [])
    entry = lists[0] if lists else result
    return format_list_entry(entry)


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
def get_domains(type: str = "deny", kind: str = "exact") -> list[dict]:
    """Get configured domain entries.

    type: "allow" (whitelist) or "deny" (blacklist).
    kind: "exact" (exact match) or "regex" (regular expression).
    """
    type = validate_domain_type(type)
    kind = validate_domain_kind(kind)
    result = _get_client().get_domains(type, kind)
    domains = result.get("domains", [])
    return [format_domain_entry(d) for d in domains]


@mcp.tool()
def add_domain(
    domain: str,
    type: str = "deny",
    kind: str = "exact",
    comment: str = "",
) -> dict:
    """Add a domain to the allow or deny list.

    domain: the domain or regex pattern to add.
    type: "allow" (whitelist) or "deny" (blacklist).
    kind: "exact" (exact domain match) or "regex" (regular expression).
    comment: optional description.
    """
    type = validate_domain_type(type)
    kind = validate_domain_kind(kind)
    result = _get_client().add_domain(domain, type, kind, comment)
    domains = result.get("domains", [])
    entry = domains[0] if domains else result
    return format_domain_entry(entry)


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
def search_domains(domain: str) -> dict:
    """Check if a domain is blocked and by which list.

    Searches gravity, antigravity, exact deny/allow, and regex deny/allow
    lists. Useful for troubleshooting why a domain is blocked or allowed.
    """
    return format_search_results(_get_client().search_domains(domain))


# ---------------------------------------------------------------------------
# DNS control + DHCP
# ---------------------------------------------------------------------------


@mcp.tool()
def get_blocking_status() -> dict:
    """Get current DNS blocking status.

    Returns whether blocking is enabled/disabled and any active timer.
    """
    return format_blocking_status(_get_client().get_blocking())


@mcp.tool()
def set_blocking(enabled: bool, timer: int | None = None) -> dict:
    """Enable or disable DNS blocking.

    enabled: True to enable, False to disable.
    timer: optional seconds before blocking auto-reverts.
           Example: set_blocking(False, 300) disables for 5 minutes.
    """
    return format_blocking_status(_get_client().set_blocking(enabled, timer))


@mcp.tool()
def get_dhcp_leases() -> list[dict]:
    """Get current DHCP leases.

    Returns active leases with IP, MAC address, hostname, and expiry time.
    """
    result = _get_client().get_dhcp_leases()
    leases = result.get("leases", [])
    return [format_lease(le) for le in leases]


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

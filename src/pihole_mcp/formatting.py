"""Response formatters for Pi-hole data."""

from typing import Any


def format_summary(
    data: dict[str, Any], blocking: dict[str, Any] | None = None
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "queries_today": data.get("queries", {}).get("total", 0),
        "blocked_today": data.get("queries", {}).get("blocked", 0),
        "percent_blocked": data.get("queries", {}).get("percent_blocked", 0),
        "domains_on_blocklist": data.get("gravity", {}).get("domains_being_blocked", 0),
        "clients_seen": data.get("clients", {}).get("total", 0),
        "unique_domains": data.get("queries", {}).get("unique_domains", 0),
        "cached": data.get("queries", {}).get("cached", 0),
        "forwarded": data.get("queries", {}).get("forwarded", 0),
    }
    if blocking is not None:
        result["blocking_enabled"] = blocking.get("blocking") == "enabled"
        result["blocking_timer"] = blocking.get("timer")
    return result


def format_query(q: dict[str, Any]) -> dict[str, Any]:
    client = q.get("client", {})
    reply = q.get("reply", {})
    return {
        "id": q.get("id"),
        "time": q.get("time"),
        "type": q.get("type"),
        "domain": q.get("domain"),
        "cname": q.get("cname"),
        "status": q.get("status"),
        "client_ip": client.get("ip"),
        "client_name": client.get("name"),
        "reply_type": reply.get("type"),
        "reply_time": reply.get("time"),
        "upstream": q.get("upstream"),
        "dnssec": q.get("dnssec"),
    }


def format_queries(data: dict[str, Any], max_entries: int = 100) -> dict[str, Any]:
    queries = data.get("queries", [])
    return {
        "cursor": data.get("cursor"),
        "records_total": data.get("recordsTotal", 0),
        "records_filtered": data.get("recordsFiltered", 0),
        "queries": [format_query(q) for q in queries[:max_entries]],
    }


def format_top_domains(data: dict[str, Any]) -> dict[str, Any]:
    domains = data.get("domains", [])
    return {
        "total_queries": data.get("total_queries", 0),
        "blocked_queries": data.get("blocked_queries", 0),
        "domains": [
            {"domain": d.get("domain"), "count": d.get("count")} for d in domains
        ],
    }


def format_top_clients(data: dict[str, Any]) -> dict[str, Any]:
    clients = data.get("clients", [])
    return {
        "total_queries": data.get("total_queries", 0),
        "blocked_queries": data.get("blocked_queries", 0),
        "clients": [
            {
                "ip": c.get("ip"),
                "name": c.get("name"),
                "count": c.get("count"),
            }
            for c in clients
        ],
    }


def format_version(data: dict[str, Any]) -> dict[str, Any]:
    versions = data.get("version", {})
    ftl = versions.get("ftl", {}).get("local", {})
    core = versions.get("core", {}).get("local", {})
    web = versions.get("web", {}).get("local", {})
    docker = versions.get("docker", {})
    return {
        "ftl": ftl.get("version"),
        "core": core.get("version"),
        "web": web.get("version"),
        "docker": docker.get("local") if isinstance(docker, dict) else docker,
        "branch": ftl.get("branch"),
        "date": ftl.get("date"),
    }


def format_list_entry(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "address": entry.get("address"),
        "enabled": entry.get("enabled", True),
        "comment": entry.get("comment", ""),
        "type": entry.get("type"),
        "groups": entry.get("groups", []),
        "id": entry.get("id"),
    }


def format_domain_entry(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "domain": entry.get("domain"),
        "type": entry.get("type"),
        "kind": entry.get("kind"),
        "enabled": entry.get("enabled", True),
        "comment": entry.get("comment", ""),
        "groups": entry.get("groups", []),
        "id": entry.get("id"),
    }


def format_search_results(data: dict[str, Any]) -> dict[str, Any]:
    search = data.get("search", {})
    params = search.get("parameters", {})
    results = search.get("results", {})
    return {
        "domain": params.get("domain"),
        "domains": search.get("domains", []),
        "gravity": search.get("gravity", []),
        "matches": {
            "domain_exact": results.get("domains", {}).get("exact", 0),
            "domain_regex": results.get("domains", {}).get("regex", 0),
            "gravity_block": results.get("gravity", {}).get("block", 0),
            "gravity_allow": results.get("gravity", {}).get("allow", 0),
            "total": results.get("total", 0),
        },
    }


def format_blocking_status(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "blocking": data.get("blocking"),
        "timer": data.get("timer"),
    }


def format_lease(lease: dict[str, Any]) -> dict[str, Any]:
    return {
        "ip": lease.get("ip"),
        "mac": lease.get("hwaddr"),
        "hostname": lease.get("name"),
        "expires": lease.get("expires"),
        "interface": lease.get("interface"),
    }

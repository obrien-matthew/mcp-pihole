"""Tests for response formatters."""

from pihole_mcp.formatting import (
    format_blocking_status,
    format_domain_entry,
    format_lease,
    format_list_entry,
    format_queries,
    format_query,
    format_search_results,
    format_summary,
    format_top_clients,
    format_top_domains,
    format_version,
)


class TestFormatSummary:
    def test_extracts_fields(self):
        data = {
            "queries": {
                "total": 12345,
                "blocked": 678,
                "percent_blocked": 5.5,
                "unique_domains": 2000,
                "cached": 3000,
                "forwarded": 9000,
            },
            "gravity": {"domains_being_blocked": 100000},
            "blocking": "enabled",
            "clients": {"total": 15},
        }
        result = format_summary(data)
        assert result["queries_today"] == 12345
        assert result["blocked_today"] == 678
        assert result["percent_blocked"] == 5.5
        assert result["domains_on_blocklist"] == 100000
        assert result["blocking_enabled"] is True
        assert result["clients_seen"] == 15
        assert result["unique_domains"] == 2000

    def test_defaults_on_empty(self):
        result = format_summary({})
        assert result["queries_today"] == 0
        assert result["blocking_enabled"] is False


class TestFormatQuery:
    def test_formats_query(self):
        q = {
            "id": 1,
            "time": 1700000000,
            "type": "A",
            "domain": "example.com",
            "cname": None,
            "status": "FORWARDED",
            "client": {"ip": "192.168.0.10", "name": "laptop"},
            "reply": {"type": "IP", "time": 25},
            "upstream": "127.0.0.1#5335",
            "dnssec": "INSECURE",
        }
        result = format_query(q)
        assert result["domain"] == "example.com"
        assert result["client_ip"] == "192.168.0.10"
        assert result["client_name"] == "laptop"
        assert result["reply_type"] == "IP"


class TestFormatQueries:
    def test_truncates_to_max(self):
        data = {
            "queries": [{"id": i, "domain": f"d{i}.com"} for i in range(200)],
            "cursor": 100,
            "recordsTotal": 200,
            "recordsFiltered": 200,
        }
        result = format_queries(data, max_entries=50)
        assert len(result["queries"]) == 50
        assert result["cursor"] == 100
        assert result["records_total"] == 200

    def test_empty_queries(self):
        result = format_queries({"queries": []})
        assert result["queries"] == []
        assert result["records_total"] == 0


class TestFormatTopDomains:
    def test_formats_domains(self):
        data = {
            "top_domains": [
                {"domain": "example.com", "count": 100},
                {"domain": "test.org", "count": 50},
            ]
        }
        result = format_top_domains(data)
        assert len(result) == 2
        assert result[0]["domain"] == "example.com"
        assert result[0]["count"] == 100

    def test_blocked_uses_top_ads_key(self):
        data = {"top_ads": [{"domain": "ads.com", "count": 200}]}
        result = format_top_domains(data)
        assert result[0]["domain"] == "ads.com"


class TestFormatTopClients:
    def test_formats_clients(self):
        data = {
            "top_clients": [
                {"ip": "192.168.0.10", "name": "laptop", "count": 500},
            ]
        }
        result = format_top_clients(data)
        assert result[0]["ip"] == "192.168.0.10"
        assert result[0]["name"] == "laptop"

    def test_empty(self):
        assert format_top_clients({}) == []


class TestFormatVersion:
    def test_formats_version(self):
        data = {
            "version": "v6.6",
            "branch": "master",
            "hash": "abc123",
            "date": "2026-04-01",
        }
        result = format_version(data)
        assert result["version"] == "v6.6"
        assert result["hash"] == "abc123"


class TestFormatListEntry:
    def test_formats_list(self):
        entry = {
            "address": "https://example.com/hosts.txt",
            "enabled": True,
            "comment": "test list",
            "type": "block",
            "groups": [0],
            "id": 1,
        }
        result = format_list_entry(entry)
        assert result["address"] == "https://example.com/hosts.txt"
        assert result["enabled"] is True
        assert result["comment"] == "test list"


class TestFormatDomainEntry:
    def test_formats_domain(self):
        entry = {
            "domain": "ads.example.com",
            "type": "deny",
            "kind": "exact",
            "enabled": True,
            "comment": "blocked",
            "groups": [0],
            "id": 5,
        }
        result = format_domain_entry(entry)
        assert result["domain"] == "ads.example.com"
        assert result["type"] == "deny"
        assert result["kind"] == "exact"


class TestFormatSearchResults:
    def test_formats_search(self):
        data = {
            "search": {
                "domain": "ads.example.com",
                "gravity": [{"address": "https://list.txt", "id": 1}],
                "antigravity": [],
                "deny": {"exact": [], "regex": []},
                "allow": {"exact": [], "regex": []},
            }
        }
        result = format_search_results(data)
        assert result["domain"] == "ads.example.com"
        assert len(result["gravity"]) == 1

    def test_empty_search(self):
        result = format_search_results({})
        assert result["gravity"] == []


class TestFormatBlockingStatus:
    def test_formats_status(self):
        result = format_blocking_status({"blocking": "enabled", "timer": None})
        assert result["blocking"] == "enabled"
        assert result["timer"] is None

    def test_with_timer(self):
        result = format_blocking_status({"blocking": "disabled", "timer": 300})
        assert result["timer"] == 300


class TestFormatLease:
    def test_formats_lease(self):
        lease = {
            "ip": "192.168.0.50",
            "hwaddr": "AA:BB:CC:DD:EE:FF",
            "name": "phone",
            "expires": 1700000000,
            "interface": "enp114s0",
        }
        result = format_lease(lease)
        assert result["ip"] == "192.168.0.50"
        assert result["mac"] == "AA:BB:CC:DD:EE:FF"
        assert result["hostname"] == "phone"

"""Tests for input validation helpers."""

import pytest

from pihole_mcp.validation import (
    validate_count,
    validate_domain_kind,
    validate_domain_type,
    validate_url,
)


class TestValidateCount:
    def test_within_range(self):
        assert validate_count(10) == 10

    def test_clamps_to_min(self):
        assert validate_count(0) == 1
        assert validate_count(-5) == 1

    def test_clamps_to_max(self):
        assert validate_count(200) == 100

    def test_custom_max(self):
        assert validate_count(60, max_val=50) == 50


class TestValidateDomainType:
    def test_allow(self):
        assert validate_domain_type("allow") == "allow"
        assert validate_domain_type("ALLOW") == "allow"

    def test_deny(self):
        assert validate_domain_type("deny") == "deny"
        assert validate_domain_type("Deny") == "deny"

    def test_invalid(self):
        with pytest.raises(ValueError, match="must be 'allow' or 'deny'"):
            validate_domain_type("block")


class TestValidateDomainKind:
    def test_exact(self):
        assert validate_domain_kind("exact") == "exact"

    def test_regex(self):
        assert validate_domain_kind("regex") == "regex"
        assert validate_domain_kind("REGEX") == "regex"

    def test_invalid(self):
        with pytest.raises(ValueError, match="must be 'exact' or 'regex'"):
            validate_domain_kind("wildcard")


class TestValidateUrl:
    def test_valid_https(self):
        assert (
            validate_url("https://example.com/hosts.txt")
            == "https://example.com/hosts.txt"
        )

    def test_valid_http(self):
        assert validate_url("http://example.com/list") == "http://example.com/list"

    def test_strips_whitespace(self):
        assert validate_url("  https://example.com  ") == "https://example.com"

    def test_empty(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_url("")

    def test_no_scheme(self):
        with pytest.raises(ValueError, match="must start with"):
            validate_url("example.com/hosts.txt")

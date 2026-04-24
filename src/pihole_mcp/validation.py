"""Input validation helpers for Pi-hole parameters."""


def validate_count(value: int, max_val: int = 100) -> int:
    """Clamp a count/limit parameter to [1, max_val]."""
    return max(1, min(value, max_val))


def validate_domain_type(value: str) -> str:
    """Validate domain type is 'allow' or 'deny'."""
    lower = value.lower()
    if lower not in ("allow", "deny"):
        raise ValueError(f"Domain type must be 'allow' or 'deny', got '{value}'.")
    return lower


def validate_domain_kind(value: str) -> str:
    """Validate domain kind is 'exact' or 'regex'."""
    lower = value.lower()
    if lower not in ("exact", "regex"):
        raise ValueError(f"Domain kind must be 'exact' or 'regex', got '{value}'.")
    return lower


def validate_url(value: str) -> str:
    """Basic validation for a blocklist URL."""
    value = value.strip()
    if not value:
        raise ValueError("URL cannot be empty.")
    if not value.startswith(("http://", "https://")):
        raise ValueError(f"URL must start with http:// or https://, got '{value}'.")
    return value

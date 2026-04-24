"""Response formatters for Pi-hole data."""

from typing import Any


def format_item(item: Any) -> dict[str, Any]:
    """Format a Pi-hole item into an LLM-friendly dict."""
    return {"raw": str(item)}

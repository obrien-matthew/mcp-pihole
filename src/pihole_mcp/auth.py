"""Pi-hole authentication and connection setup."""

import os


def get_credentials() -> dict[str, str]:
    """Load credentials from environment variables.

    Returns dict with 'url' and 'password'.
    Raises RuntimeError if PIHOLE_URL is missing.
    """
    url = os.environ.get("PIHOLE_URL", "")
    password = os.environ.get("PIHOLE_PASSWORD", "")

    if not url:
        raise RuntimeError(
            "PIHOLE_URL environment variable is required. "
            "Example: http://192.168.0.160:8080"
        )

    return {"url": url.rstrip("/"), "password": password}

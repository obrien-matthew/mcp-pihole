"""Client wrapper for the Pi-hole API."""


class Pi-holeError(Exception):
    """Pi-hole API error."""


class Pi-holeClient:
    """Validated, formatted interface to the Pi-hole API."""

    def __init__(self) -> None:
        pass

    def ping(self) -> str:
        """Placeholder method to verify the client works."""
        return "pong"

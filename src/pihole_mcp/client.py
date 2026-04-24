"""Client wrapper for the Pi-hole v6 REST API."""

import sys
from typing import Any, NoReturn
from urllib.parse import quote

import httpx

from .auth import get_credentials


class PiholeError(Exception):
    """User-facing Pi-hole API error."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class PiholeClient:
    """Validated, formatted interface to the Pi-hole v6 REST API."""

    def __init__(self) -> None:
        creds = get_credentials()
        self._base_url = creds["url"]
        self._password = creds["password"]
        self._http = httpx.Client(base_url=self._base_url, timeout=30.0)
        self._sid: str | None = None

    def _authenticate(self) -> None:
        resp = self._http.post(
            "/api/auth", json={"password": self._password}
        )
        resp.raise_for_status()
        data = resp.json()
        session = data.get("session", {})
        if not session.get("valid"):
            raise PiholeError(
                f"Authentication failed: {session.get('message', 'unknown error')}",
                status_code=401,
            )
        self._sid = session["sid"]

    def _ensure_session(self) -> None:
        if self._sid is None:
            self._authenticate()

    def _is_session_invalid(self, resp: httpx.Response) -> bool:
        if resp.status_code == 401:
            return True
        try:
            data = resp.json()
            session = data.get("session", {})
            if isinstance(session, dict) and session.get("valid") is False:
                return True
        except Exception:
            pass
        return False

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
    ) -> httpx.Response:
        self._ensure_session()
        assert self._sid is not None

        resp = self._http.request(
            method,
            path,
            params=params,
            json=json,
            headers={"X-FTL-SID": self._sid},
        )

        if self._is_session_invalid(resp):
            self._sid = None
            self._authenticate()
            assert self._sid is not None
            resp = self._http.request(
                method,
                path,
                params=params,
                json=json,
                headers={"X-FTL-SID": self._sid},
            )

        if resp.status_code >= 400:
            self._handle_http_error(resp)

        return resp

    def _handle_http_error(self, resp: httpx.Response) -> NoReturn:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        msg = f"Pi-hole API error ({resp.status_code}): {detail}"
        print(msg, file=sys.stderr)
        raise PiholeError(msg, status_code=resp.status_code)

    def _get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return self._request("GET", path, params=params).json()

    def _post(
        self, path: str, json: Any | None = None
    ) -> dict[str, Any]:
        return self._request("POST", path, json=json).json()

    def _put(
        self, path: str, json: Any | None = None
    ) -> dict[str, Any]:
        return self._request("PUT", path, json=json).json()

    def _delete(self, path: str) -> httpx.Response:
        return self._request("DELETE", path)

    @staticmethod
    def _encode_path(value: str) -> str:
        """URL-encode a value for use in a path segment."""
        return quote(value, safe="")

    def ping(self) -> dict[str, Any]:
        return self._get("/api/stats/summary")

"""Tests for the Pi-hole client."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from pihole_mcp.client import PiholeClient, PiholeError

_MOCK_REQUEST = httpx.Request("GET", "http://test")


def _auth_response(valid: bool = True, sid: str = "test-sid") -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "session": {
                "valid": valid,
                "sid": sid,
                "validity": 300,
                "message": "correct password" if valid else "wrong password",
            }
        },
        request=_MOCK_REQUEST,
    )


def _json_response(data: dict, status: int = 200) -> httpx.Response:
    return httpx.Response(status, json=data, request=_MOCK_REQUEST)


@pytest.fixture
def client():
    with patch("pihole_mcp.client.get_credentials") as mock_creds:
        mock_creds.return_value = {
            "url": "http://localhost:8080",
            "password": "testpass",
        }
        with patch.object(httpx.Client, "__init__", return_value=None):
            c = PiholeClient()
            c._http = MagicMock(spec=httpx.Client)
            return c


class TestAuthentication:
    def test_successful_auth(self, client: PiholeClient):
        client._http.post.return_value = _auth_response()
        client._authenticate()
        assert client._sid == "test-sid"
        client._http.post.assert_called_once_with(
            "/api/auth", json={"password": "testpass"}
        )

    def test_failed_auth_raises(self, client: PiholeClient):
        client._http.post.return_value = _auth_response(valid=False)
        with pytest.raises(PiholeError, match="Authentication failed"):
            client._authenticate()

    def test_ensure_session_authenticates_once(self, client: PiholeClient):
        client._http.post.return_value = _auth_response()
        client._ensure_session()
        client._ensure_session()
        assert client._http.post.call_count == 1


class TestSessionRetry:
    def test_retries_on_401(self, client: PiholeClient):
        client._http.post.return_value = _auth_response()
        expired = _json_response({}, status=401)
        success = _json_response({"data": "ok"})
        client._http.request.side_effect = [expired, success]

        result = client._get("/api/test")
        assert result == {"data": "ok"}
        assert client._http.request.call_count == 2

    def test_retries_on_session_invalid_body(self, client: PiholeClient):
        client._http.post.return_value = _auth_response()
        invalid_session = _json_response(
            {"session": {"valid": False}}, status=200
        )
        success = _json_response({"data": "ok"})
        client._http.request.side_effect = [invalid_session, success]

        result = client._get("/api/test")
        assert result == {"data": "ok"}

    def test_raises_on_persistent_error(self, client: PiholeClient):
        client._http.post.return_value = _auth_response()
        error = _json_response({"error": "not found"}, status=404)
        client._http.request.return_value = error

        with pytest.raises(PiholeError, match="404"):
            client._get("/api/missing")


class TestConvenienceMethods:
    def test_get(self, client: PiholeClient):
        client._http.post.return_value = _auth_response()
        client._http.request.return_value = _json_response({"key": "val"})
        result = client._get("/api/test", params={"a": "1"})
        assert result == {"key": "val"}

    def test_post(self, client: PiholeClient):
        client._http.post.return_value = _auth_response()
        client._http.request.return_value = _json_response({"created": True})
        result = client._post("/api/test", json={"name": "x"})
        assert result == {"created": True}

    def test_delete(self, client: PiholeClient):
        client._http.post.return_value = _auth_response()
        client._http.request.return_value = httpx.Response(204, request=_MOCK_REQUEST)
        resp = client._delete("/api/test")
        assert resp.status_code == 204


class TestEncodePath:
    def test_encodes_slashes(self):
        assert PiholeClient._encode_path("https://example.com/list.txt") == (
            "https%3A%2F%2Fexample.com%2Flist.txt"
        )

    def test_encodes_special_chars(self):
        result = PiholeClient._encode_path("a b&c=d")
        assert "%" in result
        assert " " not in result


class TestMissingCredentials:
    def test_missing_url_raises(self):
        with (
            patch.dict("os.environ", {}, clear=True),
            pytest.raises(RuntimeError, match="PIHOLE_URL"),
        ):
            PiholeClient()

    def test_empty_password_allowed(self):
        with patch.dict(
            "os.environ",
            {"PIHOLE_URL": "http://localhost:8080", "PIHOLE_PASSWORD": ""},
        ), patch.object(httpx.Client, "__init__", return_value=None):
            c = PiholeClient()
            assert c._password == ""

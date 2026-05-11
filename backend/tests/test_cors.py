import typing as tp
import fastapi.testclient as fastapi_testclient

from app import main as app_main


class _HasHeaders(tp.Protocol):
    headers: tp.Mapping[str, str]


def _assert_cors_headers(resp: _HasHeaders, origin: str) -> None:
    assert resp.headers.get("access-control-allow-origin") == origin
    assert resp.headers.get("access-control-allow-credentials") == "true"
    # Exposed header(s) should be present even if not returned by endpoint.
    assert "x-request-id" in resp.headers.get("access-control-expose-headers", "").lower()


def test_cors_allows_localhost_and_ipv4_loopback_for_get() -> None:
    client = fastapi_testclient.TestClient(app_main.app)

    for origin in ("http://localhost", "http://127.0.0.1", "http://localhost:5173", "http://127.0.0.1:5173"):
        resp = client.get("/", headers={"Origin": origin})
        assert resp.status_code == 200
        _assert_cors_headers(resp, origin)


def test_cors_preflight_allows_auth_headers() -> None:
    client = fastapi_testclient.TestClient(app_main.app)
    origin = "http://127.0.0.1:5173"

    resp = client.options(
        "/api/v1/auth/login",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type,x-request-id",
        },
    )

    # Starlette CORS middleware returns 200 for valid preflight.
    assert resp.status_code == 200
    _assert_cors_headers(resp, origin)

    allow_headers = resp.headers.get("access-control-allow-headers", "").lower()
    assert "authorization" in allow_headers
    assert "content-type" in allow_headers
    assert "x-request-id" in allow_headers


"""
Tests for websocket auth helpers.
"""

from app.realtime import auth as realtime_auth


def test_extract_bearer_token():
    assert realtime_auth.extract_bearer_token(None) is None
    assert realtime_auth.extract_bearer_token("") is None
    assert realtime_auth.extract_bearer_token("Basic abc") is None
    assert realtime_auth.extract_bearer_token("Bearer") is None
    assert realtime_auth.extract_bearer_token("Bearer token123") == "token123"
    assert realtime_auth.extract_bearer_token("bearer token123") == "token123"


def test_extract_websocket_token_prefers_query_param():
    class DummyWebSocket:
        def __init__(self):
            self.query_params = {"token": "from_query"}
            self.headers = {"authorization": "Bearer from_header"}

    ws = DummyWebSocket()
    assert realtime_auth.extract_websocket_token(ws) == "from_query"


def test_extract_websocket_token_falls_back_to_header():
    class DummyWebSocket:
        def __init__(self):
            self.query_params = {}
            self.headers = {"authorization": "Bearer from_header"}

    ws = DummyWebSocket()
    assert realtime_auth.extract_websocket_token(ws) == "from_header"


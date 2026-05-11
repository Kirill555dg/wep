"""
Tests for ConnectionManager.
"""

import pytest

from app.realtime import connection_manager as connection_manager_module


pytestmark = pytest.mark.anyio


class DummyWebSocket:
    def __init__(self, *, fail: bool = False):
        self.fail = fail
        self.sent: list[dict[str, object]] = []

    async def send_json(self, payload):
        if self.fail:
            raise RuntimeError("send failed")
        self.sent.append(payload)


async def test_connection_manager_connect_broadcast_disconnect():
    manager = connection_manager_module.ConnectionManager()

    ws_ok = DummyWebSocket()
    ws_fail = DummyWebSocket(fail=True)

    await manager.connect(1, ws_ok)
    await manager.connect(1, ws_fail)

    assert await manager.count(1) == 2

    await manager.broadcast_json(1, {"type": "message"})
    assert ws_ok.sent == [{"type": "message"}]

    # Failed socket should be removed.
    assert await manager.count(1) == 1

    await manager.disconnect(1, ws_ok)
    assert await manager.count(1) == 0


"""
WebSocket connection manager for chat rooms.
"""

import asyncio
import logging
import typing as tp

import fastapi


logger = logging.getLogger("app.realtime.connection_manager")


class ConnectionManager:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._connections: dict[int, set[fastapi.WebSocket]] = {}

    async def connect(self, classroom_id: int, websocket: fastapi.WebSocket) -> None:
        async with self._lock:
            bucket = self._connections.setdefault(classroom_id, set())
            bucket.add(websocket)
            logger.info(
                "ws_connected",
                extra={"classroom_id": classroom_id, "connections": len(bucket)},
            )

    async def disconnect(self, classroom_id: int, websocket: fastapi.WebSocket) -> int:
        async with self._lock:
            bucket = self._connections.get(classroom_id)
            if not bucket:
                return 0

            bucket.discard(websocket)
            count = len(bucket)
            if count == 0:
                self._connections.pop(classroom_id, None)

            logger.info(
                "ws_disconnected",
                extra={"classroom_id": classroom_id, "connections": count},
            )
            return count

    async def count(self, classroom_id: int) -> int:
        async with self._lock:
            bucket = self._connections.get(classroom_id)
            return len(bucket) if bucket else 0

    async def broadcast_json(self, classroom_id: int, payload: dict[str, tp.Any]) -> None:
        async with self._lock:
            recipients = list(self._connections.get(classroom_id, set()))

        if not recipients:
            return

        stale: list[fastapi.WebSocket] = []
        for ws in recipients:
            try:
                await ws.send_json(payload)
            except Exception:
                stale.append(ws)

        if stale:
            async with self._lock:
                bucket = self._connections.get(classroom_id)
                if not bucket:
                    return
                for ws in stale:
                    bucket.discard(ws)
                if not bucket:
                    self._connections.pop(classroom_id, None)


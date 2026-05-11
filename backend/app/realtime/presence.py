"""
Ephemeral chat state (presence/typing) stored in Redis.

These events are not persisted in Postgres.
"""

import logging

import redis.asyncio as redis_asyncio


logger = logging.getLogger("app.realtime.presence")


class ChatEphemeralStore:
    def __init__(
        self,
        redis: redis_asyncio.Redis,
        *,
        presence_ttl_seconds: int,
        typing_ttl_seconds: int,
    ) -> None:
        self._redis = redis
        self._presence_ttl = int(presence_ttl_seconds)
        self._typing_ttl = int(typing_ttl_seconds)

    def _presence_set_key(self, classroom_id: int) -> str:
        return f"wep:chat:presence:{classroom_id}"

    def _presence_key(self, classroom_id: int, user_id: int) -> str:
        return f"wep:chat:presence:{classroom_id}:{user_id}"

    def _typing_set_key(self, classroom_id: int) -> str:
        return f"wep:chat:typing:{classroom_id}"

    def _typing_key(self, classroom_id: int, user_id: int) -> str:
        return f"wep:chat:typing:{classroom_id}:{user_id}"

    async def set_online(self, classroom_id: int, user_id: int) -> None:
        await self._redis.sadd(self._presence_set_key(classroom_id), str(user_id))
        await self._redis.set(self._presence_key(classroom_id, user_id), "1", ex=self._presence_ttl)

    async def touch_online(self, classroom_id: int, user_id: int) -> None:
        await self._redis.set(self._presence_key(classroom_id, user_id), "1", ex=self._presence_ttl)

    async def set_offline(self, classroom_id: int, user_id: int) -> None:
        await self._redis.srem(self._presence_set_key(classroom_id), str(user_id))
        await self._redis.delete(self._presence_key(classroom_id, user_id))
        # Also stop typing on disconnect.
        await self.stop_typing(classroom_id, user_id)

    async def list_online(self, classroom_id: int) -> list[int]:
        raw = await self._redis.smembers(self._presence_set_key(classroom_id))
        ids: list[int] = []
        stale: list[str] = []

        for item in raw:
            text = item.decode() if isinstance(item, (bytes, bytearray)) else str(item)
            try:
                user_id = int(text)
            except Exception:
                stale.append(text)
                continue

            exists = await self._redis.exists(self._presence_key(classroom_id, user_id))
            if int(exists) > 0:
                ids.append(user_id)
            else:
                stale.append(text)

        if stale:
            await self._redis.srem(self._presence_set_key(classroom_id), *stale)

        ids.sort()
        return ids

    async def start_typing(self, classroom_id: int, user_id: int) -> None:
        await self._redis.sadd(self._typing_set_key(classroom_id), str(user_id))
        await self._redis.set(self._typing_key(classroom_id, user_id), "1", ex=self._typing_ttl)

    async def stop_typing(self, classroom_id: int, user_id: int) -> None:
        await self._redis.srem(self._typing_set_key(classroom_id), str(user_id))
        await self._redis.delete(self._typing_key(classroom_id, user_id))

    async def list_typing(self, classroom_id: int) -> list[int]:
        raw = await self._redis.smembers(self._typing_set_key(classroom_id))
        ids: list[int] = []
        stale: list[str] = []

        for item in raw:
            text = item.decode() if isinstance(item, (bytes, bytearray)) else str(item)
            try:
                user_id = int(text)
            except Exception:
                stale.append(text)
                continue

            exists = await self._redis.exists(self._typing_key(classroom_id, user_id))
            if int(exists) > 0:
                ids.append(user_id)
            else:
                stale.append(text)

        if stale:
            await self._redis.srem(self._typing_set_key(classroom_id), *stale)

        ids.sort()
        return ids


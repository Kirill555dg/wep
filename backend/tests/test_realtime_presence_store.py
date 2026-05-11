"""
Tests for ChatEphemeralStore (presence/typing) using FakeRedis.
"""

import pytest

from app.realtime import presence as presence_module


pytestmark = pytest.mark.anyio


class FakeRedis:
    def __init__(self) -> None:
        self._kv: dict[str, str] = {}
        self._sets: dict[str, set[str]] = {}

    async def sadd(self, key: str, *values: str) -> int:
        bucket = self._sets.setdefault(key, set())
        before = len(bucket)
        for v in values:
            bucket.add(str(v))
        return len(bucket) - before

    async def srem(self, key: str, *values: str) -> int:
        bucket = self._sets.setdefault(key, set())
        removed = 0
        for v in values:
            if str(v) in bucket:
                bucket.remove(str(v))
                removed += 1
        return removed

    async def smembers(self, key: str):
        return set(self._sets.get(key, set()))

    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        self._kv[key] = str(value)
        return True

    async def delete(self, key: str) -> int:
        existed = 1 if key in self._kv else 0
        self._kv.pop(key, None)
        return existed

    async def exists(self, key: str) -> int:
        return 1 if key in self._kv else 0


async def test_presence_store_online_filters_stale_members():
    redis = FakeRedis()
    store = presence_module.ChatEphemeralStore(redis, presence_ttl_seconds=60, typing_ttl_seconds=6)

    await store.set_online(10, 1)
    await store.set_online(10, 2)

    # Inject stale member into the set (no corresponding key).
    await redis.sadd("wep:chat:presence:10", "999")

    online = await store.list_online(10)
    assert online == [1, 2]
    # Stale should be removed from set.
    assert "999" not in await redis.smembers("wep:chat:presence:10")


async def test_presence_store_typing_stops_on_offline():
    redis = FakeRedis()
    store = presence_module.ChatEphemeralStore(redis, presence_ttl_seconds=60, typing_ttl_seconds=6)

    await store.set_online(10, 1)
    await store.start_typing(10, 1)

    assert await store.list_typing(10) == [1]

    await store.set_offline(10, 1)
    assert await store.list_online(10) == []
    assert await store.list_typing(10) == []


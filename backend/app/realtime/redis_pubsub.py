"""
Redis Pub/Sub broker for cross-instance chat fanout.
"""

import asyncio
import json
import logging
import typing as tp

import redis.asyncio as redis_asyncio

from app.realtime import connection_manager as connection_manager_module


logger = logging.getLogger("app.realtime.redis_pubsub")


def classroom_channel(classroom_id: int) -> str:
    return f"chat.classroom.{classroom_id}"


class RedisPubSubBroker:
    def __init__(
        self,
        redis: redis_asyncio.Redis,
        *,
        manager: connection_manager_module.ConnectionManager,
    ) -> None:
        self._redis = redis
        self._manager = manager
        self._lock = asyncio.Lock()
        self._tasks: dict[int, asyncio.Task[None]] = {}
        self._refcounts: dict[int, int] = {}

    async def publish(self, classroom_id: int, payload: dict[str, tp.Any]) -> None:
        channel = classroom_channel(classroom_id)
        await self._redis.publish(channel, json.dumps(payload, ensure_ascii=False))
        logger.debug("redis_published", extra={"channel": channel})

    async def ensure_subscription(self, classroom_id: int) -> None:
        async with self._lock:
            self._refcounts[classroom_id] = self._refcounts.get(classroom_id, 0) + 1
            if classroom_id in self._tasks:
                return

            task = asyncio.create_task(self._run_subscription(classroom_id))
            self._tasks[classroom_id] = task

    async def release_subscription(self, classroom_id: int) -> None:
        async with self._lock:
            current = self._refcounts.get(classroom_id, 0)
            if current <= 1:
                self._refcounts.pop(classroom_id, None)
                task = self._tasks.pop(classroom_id, None)
                if task:
                    task.cancel()
            else:
                self._refcounts[classroom_id] = current - 1

    async def shutdown(self) -> None:
        async with self._lock:
            tasks = list(self._tasks.values())
            self._tasks.clear()
            self._refcounts.clear()

        for task in tasks:
            task.cancel()
        for task in tasks:
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception:
                pass

    async def _run_subscription(self, classroom_id: int) -> None:
        channel = classroom_channel(classroom_id)
        pubsub = self._redis.pubsub()
        try:
            await pubsub.subscribe(channel)
            logger.info("redis_subscribed", extra={"channel": channel})

            async for msg in pubsub.listen():
                if not isinstance(msg, dict):
                    continue
                if msg.get("type") != "message":
                    continue

                data = msg.get("data")
                if isinstance(data, (bytes, bytearray)):
                    text = data.decode("utf-8", errors="replace")
                else:
                    text = str(data)

                try:
                    payload = tp.cast(dict[str, tp.Any], json.loads(text))
                except Exception:
                    logger.warning("redis_message_invalid_json", extra={"channel": channel})
                    continue

                await self._manager.broadcast_json(classroom_id, payload)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("redis_subscription_failed", extra={"channel": channel})
        finally:
            try:
                await pubsub.unsubscribe(channel)
            except Exception:
                pass
            try:
                await pubsub.close()
            except Exception:
                pass
            logger.info("redis_unsubscribed", extra={"channel": channel})


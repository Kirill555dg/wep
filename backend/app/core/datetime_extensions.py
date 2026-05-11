"""
Datetime helpers.

We standardize on timezone-aware UTC datetimes and avoid `datetime.utcnow()`
which produces a naive datetime with a misleading name.
"""

import datetime
import functools
import inspect
import logging
import typing as tp


def utc_now() -> datetime.datetime:
    """Just a shorthand for UTC timezone-aware datetime object."""
    return datetime.datetime.now(tz=datetime.timezone.utc)


def utc_timestamp_f(dt_obj: datetime.datetime | None = None) -> float:
    """
    UTC timestamp as float for a given datetime object
    or current time if `dt_obj` is omitted.

    Please never use datetime's `utcnow` method, it has misleading name.
    """
    if dt_obj is None:
        return utc_now().timestamp()

    if dt_obj.tzinfo is None:
        dt_obj = dt_obj.replace(tzinfo=datetime.timezone.utc)

    return dt_obj.timestamp()


def utc_timestamp(dt_obj: datetime.datetime | None = None) -> int:
    """
    UTC timestamp as integer for a given datetime object
    or current time if `dt_obj` is omitted.
    """
    return int(utc_timestamp_f(dt_obj))


def utc_timestamp_ms(dt_obj: datetime.datetime | None = None) -> int:
    """
    UTC timestamp in milliseconds as integer
    for a given datetime object
    or current time if `dt_obj` is omitted.
    """
    return int(utc_timestamp_f(dt_obj) * 1000)


def from_utc_timestamp(timestamp: int) -> datetime.datetime:
    """Convert UTC timestamp to datetime object."""
    return datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)


def log_time(logger: logging.Logger) -> tp.Callable[[tp.Callable[..., tp.Any]], tp.Callable[..., tp.Any]]:
    """Log execution time for sync/async functions."""

    def decorator(func: tp.Callable[..., tp.Any]) -> tp.Callable[..., tp.Any]:
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: tp.Any, **kwargs: tp.Any) -> tp.Any:
                start_time = utc_timestamp_f()
                result = await func(*args, **kwargs)
                end_time = utc_timestamp_f()
                execution_time = end_time - start_time
                logger.info(
                    "Function '%s' took %.4f seconds to execute",
                    func.__name__,
                    execution_time,
                )
                return result

            return async_wrapper

        @functools.wraps(func)
        def wrapper(*args: tp.Any, **kwargs: tp.Any) -> tp.Any:
            start_time = utc_timestamp_f()
            result = func(*args, **kwargs)
            end_time = utc_timestamp_f()
            execution_time = end_time - start_time
            logger.info(
                "Function '%s' took %.4f seconds to execute",
                func.__name__,
                execution_time,
            )
            return result

        return wrapper

    return decorator


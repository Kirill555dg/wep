"""
Request-scoped context values.

Used for correlating logs with a request_id.
"""

import contextvars


request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


def get_request_id() -> str:
    return request_id_var.get()


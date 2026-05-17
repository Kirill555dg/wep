"""
Fuzz test infrastructure.

Each fuzz test function gets a fresh PostgreSQL schema via the http_client
fixture inherited from the parent conftest. The schema is created before
the test and dropped after — all Hypothesis examples within one test run
inside the same schema, which is acceptable for "no 500" properties.
"""

# Re-export anyio_backend so this sub-package also defaults to asyncio.
# The parent conftest already sets it at session scope; this is a safety net.

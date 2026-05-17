"""
Fuzzing tests using Hypothesis property-based testing.

Invariant: the API must NEVER return HTTP 500 for any input.
Valid responses for unexpected input: 400, 401, 403, 404, 409, 422.

Each test function runs in an isolated database schema (via http_client fixture).
All Hypothesis examples within one test share that schema — this is intentional:
the http_client fixture is function-scoped, so the schema lives for the duration
of one test function (covering all generated examples).

Run separately:
    uv run pytest tests/fuzz/ -v
"""

import uuid

import httpx
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

pytestmark = pytest.mark.anyio

NEVER_500 = {200, 201, 400, 401, 403, 404, 409, 422}

SQL_INJECTION_PAYLOADS = [
    "'; DROP TABLE tests; --",
    "' OR '1'='1",
    "1; SELECT * FROM users",
    "UNION SELECT * FROM login_data",
    "' AND 1=1--",
]

XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "javascript:alert(1)",
    '"><img src=x onerror=alert(1)>',
    "<svg/onload=alert(1)>",
]

# Hypothesis settings for integration fuzz tests:
# - deadline=None: real HTTP requests are slower than the 200ms default
# - function_scoped_fixture: intentionally shared schema across examples
_SUPPRESS = [HealthCheck.too_slow, HealthCheck.function_scoped_fixture]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _register_and_login(client: httpx.AsyncClient) -> str:
    """Register a unique user and return a valid JWT."""
    email = f"fuzz_{uuid.uuid4().hex[:12]}@example.com"
    await client.post("/api/v1/auth/register", json={
        "email": email, "password": "FuzzPass1!",
        "first_name": "F", "last_name": "Z", "role": "student",
    })
    resp = await client.post("/api/v1/auth/login", json={"username_or_email": email, "password": "FuzzPass1!"})
    return resp.json().get("access_token", "")


# ---------------------------------------------------------------------------
# Authentication endpoints
# ---------------------------------------------------------------------------

@given(
    email=st.emails(),
    password=st.text(min_size=8, max_size=64, alphabet=st.characters(blacklist_categories=("Cs",))),
    first_name=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=("Cs",))),
    last_name=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=("Cs",))),
)
@settings(max_examples=30, suppress_health_check=_SUPPRESS, deadline=None)
async def test_fuzz_register(
    http_client: httpx.AsyncClient, email: str, password: str, first_name: str, last_name: str
) -> None:
    resp = await http_client.post("/api/v1/auth/register", json={
        "email": email, "password": password,
        "first_name": first_name, "last_name": last_name, "role": "student",
    })
    assert resp.status_code in NEVER_500, f"500 on register: {resp.text}"


@given(
    username_or_email=st.text(min_size=0, max_size=300),
    password=st.text(min_size=0, max_size=300),
)
@settings(max_examples=30, suppress_health_check=_SUPPRESS, deadline=None)
async def test_fuzz_login(http_client: httpx.AsyncClient, username_or_email: str, password: str) -> None:
    resp = await http_client.post("/api/v1/auth/login", json={
        "username_or_email": username_or_email, "password": password,
    })
    assert resp.status_code in NEVER_500, f"500 on login: {resp.text}"


# ---------------------------------------------------------------------------
# Test CRUD
# ---------------------------------------------------------------------------

@given(
    title=st.text(min_size=0, max_size=512),
    description=st.one_of(st.none(), st.text(max_size=4096)),
    is_public=st.booleans(),
    time_limit=st.one_of(st.none(), st.integers(min_value=-100, max_value=1_000_000)),
)
@settings(max_examples=30, suppress_health_check=_SUPPRESS, deadline=None)
async def test_fuzz_create_test(
    http_client: httpx.AsyncClient, title: str, description: str | None, is_public: bool, time_limit: int | None
) -> None:
    token = await _register_and_login(http_client)
    resp = await http_client.post("/api/v1/tests/", json={
        "title": title, "description": description, "is_public": is_public, "time_limit_minutes": time_limit,
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code in NEVER_500, f"500 on create_test: {resp.text}"


@given(test_id=st.integers(min_value=-1_000_000, max_value=1_000_000))
@settings(max_examples=20, suppress_health_check=_SUPPRESS, deadline=None)
async def test_fuzz_get_test_random_id(http_client: httpx.AsyncClient, test_id: int) -> None:
    token = await _register_and_login(http_client)
    resp = await http_client.get(f"/api/v1/tests/{test_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code in NEVER_500, f"500 on get_test({test_id}): {resp.text}"


# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------

@given(q=st.one_of(st.none(), st.text(max_size=200)))
@settings(max_examples=20, suppress_health_check=_SUPPRESS, deadline=None)
async def test_fuzz_catalog_search(http_client: httpx.AsyncClient, q: str | None) -> None:
    params = {"q": q} if q is not None else {}
    resp = await http_client.get("/api/v1/catalog/", params=params)
    assert resp.status_code in NEVER_500, f"500 on catalog search: {resp.text}"


@given(test_id=st.integers(min_value=-100, max_value=100))
@settings(max_examples=20, suppress_health_check=_SUPPRESS, deadline=None)
async def test_fuzz_get_catalog_test(http_client: httpx.AsyncClient, test_id: int) -> None:
    resp = await http_client.get(f"/api/v1/catalog/{test_id}")
    assert resp.status_code in NEVER_500, f"500 on catalog({test_id}): {resp.text}"


# ---------------------------------------------------------------------------
# Attempts
# ---------------------------------------------------------------------------

@given(test_id=st.integers(min_value=-100, max_value=100))
@settings(max_examples=20, suppress_health_check=_SUPPRESS, deadline=None)
async def test_fuzz_start_attempt(http_client: httpx.AsyncClient, test_id: int) -> None:
    token = await _register_and_login(http_client)
    resp = await http_client.post(
        "/api/v1/attempts/", json={"test_id": test_id}, headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code in NEVER_500, f"500 on start_attempt({test_id}): {resp.text}"


@given(
    attempt_id=st.integers(min_value=-100, max_value=100),
    question_id=st.integers(min_value=-100, max_value=100),
    selected=st.one_of(st.none(), st.lists(st.integers(min_value=-100, max_value=100), max_size=10)),
    text=st.one_of(st.none(), st.text(max_size=1000)),
)
@settings(max_examples=20, suppress_health_check=_SUPPRESS, deadline=None)
async def test_fuzz_submit_answer(
    http_client: httpx.AsyncClient,
    attempt_id: int,
    question_id: int,
    selected: list[int] | None,
    text: str | None,
) -> None:
    token = await _register_and_login(http_client)
    resp = await http_client.post(
        f"/api/v1/attempts/{attempt_id}/answers",
        json={"question_id": question_id, "selected_option_ids": selected, "text_answer": text},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code in NEVER_500, f"500 on submit_answer: {resp.text}"


# ---------------------------------------------------------------------------
# Malicious input (SQL injection / XSS)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS + XSS_PAYLOADS)
async def test_malicious_input_in_title(http_client: httpx.AsyncClient, payload: str) -> None:
    token = await _register_and_login(http_client)
    resp = await http_client.post(
        "/api/v1/tests/", json={"title": payload, "is_public": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code in NEVER_500, f"500 on malicious title: {resp.text}"


@pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS + XSS_PAYLOADS)
async def test_malicious_input_in_login(http_client: httpx.AsyncClient, payload: str) -> None:
    resp = await http_client.post("/api/v1/auth/login", json={
        "username_or_email": payload, "password": payload,
    })
    assert resp.status_code in NEVER_500, f"500 on malicious login: {resp.text}"


@pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS + XSS_PAYLOADS)
async def test_malicious_input_in_catalog_search(http_client: httpx.AsyncClient, payload: str) -> None:
    resp = await http_client.get("/api/v1/catalog/", params={"q": payload})
    assert resp.status_code in NEVER_500, f"500 on malicious search: {resp.text}"


# ---------------------------------------------------------------------------
# Boundary values (schema validation)
# ---------------------------------------------------------------------------

async def test_empty_title_rejected(http_client: httpx.AsyncClient) -> None:
    token = await _register_and_login(http_client)
    resp = await http_client.post(
        "/api/v1/tests/", json={"title": "", "is_public": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


async def test_very_long_title_rejected(http_client: httpx.AsyncClient) -> None:
    token = await _register_and_login(http_client)
    resp = await http_client.post(
        "/api/v1/tests/", json={"title": "A" * 10000, "is_public": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


async def test_negative_time_limit_rejected(http_client: httpx.AsyncClient) -> None:
    token = await _register_and_login(http_client)
    resp = await http_client.post(
        "/api/v1/tests/", json={"title": "T", "time_limit_minutes": -1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


async def test_zero_time_limit_rejected(http_client: httpx.AsyncClient) -> None:
    token = await _register_and_login(http_client)
    resp = await http_client.post(
        "/api/v1/tests/", json={"title": "T", "time_limit_minutes": 0},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422

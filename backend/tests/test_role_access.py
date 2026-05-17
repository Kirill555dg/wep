"""
Role model validation: ownership and access control through the HTTP API.
All tests run against an isolated per-function database schema.
"""

import uuid

import httpx
import pytest

pytestmark = pytest.mark.anyio


def _uid() -> str:
    return uuid.uuid4().hex[:8]


async def _register_and_login(client: httpx.AsyncClient, prefix: str = "u") -> str:
    email = f"{prefix}_{_uid()}@test.com"
    await client.post("/api/v1/auth/register", json={
        "email": email, "password": "Pass1234!",
        "first_name": "T", "last_name": "U", "role": "student",
    })
    resp = await client.post("/api/v1/auth/login", json={"username_or_email": email, "password": "Pass1234!"})
    return resp.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def _create_test(client: httpx.AsyncClient, token: str, is_public: bool = False) -> dict:
    resp = await client.post("/api/v1/tests/", json={"title": "T", "is_public": is_public}, headers=_auth(token))
    assert resp.status_code == 201
    return resp.json()


# ---------- unauthenticated ----------

async def test_unauthenticated_cannot_create_test(http_client: httpx.AsyncClient) -> None:
    resp = await http_client.post("/api/v1/tests/", json={"title": "T", "is_public": False})
    assert resp.status_code == 403


async def test_unauthenticated_cannot_start_attempt(http_client: httpx.AsyncClient) -> None:
    resp = await http_client.post("/api/v1/attempts/", json={"test_id": 1})
    assert resp.status_code == 403


async def test_unauthenticated_cannot_see_own_tests(http_client: httpx.AsyncClient) -> None:
    resp = await http_client.get("/api/v1/tests/")
    assert resp.status_code == 403


async def test_unauthenticated_cannot_upload_media(http_client: httpx.AsyncClient) -> None:
    resp = await http_client.post("/api/v1/media/upload", files={"file": ("a.png", b"data", "image/png")})
    assert resp.status_code == 403


async def test_invalid_token_rejected(http_client: httpx.AsyncClient) -> None:
    resp = await http_client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert resp.status_code == 401


async def test_no_token_rejected(http_client: httpx.AsyncClient) -> None:
    resp = await http_client.get("/api/v1/auth/me")
    assert resp.status_code == 403


# ---------- ownership ----------

async def test_cannot_update_others_test(http_client: httpx.AsyncClient) -> None:
    owner = await _register_and_login(http_client, "owner")
    other = await _register_and_login(http_client, "other")
    test = await _create_test(http_client, owner)
    resp = await http_client.patch(f"/api/v1/tests/{test['id']}", json={"title": "Hacked"}, headers=_auth(other))
    assert resp.status_code == 403


async def test_cannot_delete_others_test(http_client: httpx.AsyncClient) -> None:
    owner = await _register_and_login(http_client, "owner")
    other = await _register_and_login(http_client, "other")
    test = await _create_test(http_client, owner)
    resp = await http_client.delete(f"/api/v1/tests/{test['id']}", headers=_auth(other))
    assert resp.status_code == 403


async def test_cannot_add_question_to_others_test(http_client: httpx.AsyncClient) -> None:
    owner = await _register_and_login(http_client, "owner")
    other = await _register_and_login(http_client, "other")
    test = await _create_test(http_client, owner)
    resp = await http_client.post(
        f"/api/v1/tests/{test['id']}/questions",
        json={"question_type": "text", "text": "Q", "points": 1},
        headers=_auth(other),
    )
    assert resp.status_code == 403


async def test_cannot_view_stats_for_others_test(http_client: httpx.AsyncClient) -> None:
    owner = await _register_and_login(http_client, "owner")
    other = await _register_and_login(http_client, "other")
    test = await _create_test(http_client, owner)
    resp = await http_client.get(f"/api/v1/stats/tests/{test['id']}", headers=_auth(other))
    assert resp.status_code == 403


# ---------- private test visibility ----------

async def test_private_test_hidden_from_others(http_client: httpx.AsyncClient) -> None:
    owner = await _register_and_login(http_client, "owner")
    other = await _register_and_login(http_client, "other")
    test = await _create_test(http_client, owner, is_public=False)
    resp = await http_client.get(f"/api/v1/tests/{test['id']}", headers=_auth(other))
    assert resp.status_code == 403


async def test_private_test_not_in_catalog(http_client: httpx.AsyncClient) -> None:
    owner = await _register_and_login(http_client, "owner")
    test = await _create_test(http_client, owner, is_public=False)
    resp = await http_client.get("/api/v1/catalog/")
    assert resp.status_code == 200
    ids = [t["id"] for t in resp.json()]
    assert test["id"] not in ids


async def test_public_test_visible_without_auth(http_client: httpx.AsyncClient) -> None:
    owner = await _register_and_login(http_client, "owner")
    test = await _create_test(http_client, owner, is_public=True)
    resp = await http_client.get(f"/api/v1/catalog/{test['id']}")
    assert resp.status_code == 200


async def test_public_test_visible_to_any_user(http_client: httpx.AsyncClient) -> None:
    owner = await _register_and_login(http_client, "owner")
    reader = await _register_and_login(http_client, "reader")
    test = await _create_test(http_client, owner, is_public=True)
    resp = await http_client.get(f"/api/v1/tests/{test['id']}", headers=_auth(reader))
    assert resp.status_code == 200


async def test_author_sees_own_private_test(http_client: httpx.AsyncClient) -> None:
    owner = await _register_and_login(http_client, "owner")
    test = await _create_test(http_client, owner, is_public=False)
    resp = await http_client.get(f"/api/v1/tests/{test['id']}", headers=_auth(owner))
    assert resp.status_code == 200


# ---------- attempt isolation ----------

async def test_cannot_finish_others_attempt(http_client: httpx.AsyncClient) -> None:
    owner = await _register_and_login(http_client, "owner")
    other = await _register_and_login(http_client, "other")
    test = await _create_test(http_client, owner, is_public=True)
    start = await http_client.post("/api/v1/attempts/", json={"test_id": test["id"]}, headers=_auth(owner))
    assert start.status_code == 201
    attempt_id = start.json()["id"]
    resp = await http_client.post(f"/api/v1/attempts/{attempt_id}/finish", headers=_auth(other))
    assert resp.status_code == 404


async def test_cannot_submit_to_others_attempt(http_client: httpx.AsyncClient) -> None:
    owner = await _register_and_login(http_client, "owner")
    other = await _register_and_login(http_client, "other")
    test = await _create_test(http_client, owner, is_public=True)
    start = await http_client.post("/api/v1/attempts/", json={"test_id": test["id"]}, headers=_auth(owner))
    attempt_id = start.json()["id"]
    resp = await http_client.post(
        f"/api/v1/attempts/{attempt_id}/answers", json={"question_id": 1}, headers=_auth(other)
    )
    assert resp.status_code == 404


async def test_cannot_get_others_attempt_result(http_client: httpx.AsyncClient) -> None:
    owner = await _register_and_login(http_client, "owner")
    other = await _register_and_login(http_client, "other")
    test = await _create_test(http_client, owner, is_public=True)
    start = await http_client.post("/api/v1/attempts/", json={"test_id": test["id"]}, headers=_auth(owner))
    attempt_id = start.json()["id"]
    await http_client.post(f"/api/v1/attempts/{attempt_id}/finish", headers=_auth(owner))
    resp = await http_client.get(f"/api/v1/attempts/{attempt_id}/result", headers=_auth(other))
    assert resp.status_code == 404


async def test_cannot_start_duplicate_active_attempt(http_client: httpx.AsyncClient) -> None:
    tok = await _register_and_login(http_client)
    test = await _create_test(http_client, tok, is_public=True)
    r1 = await http_client.post("/api/v1/attempts/", json={"test_id": test["id"]}, headers=_auth(tok))
    assert r1.status_code == 201
    r2 = await http_client.post("/api/v1/attempts/", json={"test_id": test["id"]}, headers=_auth(tok))
    assert r2.status_code == 400


# ---------- 404 for nonexistent resources ----------

async def test_404_for_nonexistent_test(http_client: httpx.AsyncClient) -> None:
    tok = await _register_and_login(http_client)
    resp = await http_client.get("/api/v1/tests/999999", headers=_auth(tok))
    assert resp.status_code == 404


async def test_404_for_nonexistent_attempt_submit(http_client: httpx.AsyncClient) -> None:
    tok = await _register_and_login(http_client)
    resp = await http_client.post("/api/v1/attempts/999999/answers", json={"question_id": 1}, headers=_auth(tok))
    assert resp.status_code == 404


async def test_404_for_nonexistent_catalog_test(http_client: httpx.AsyncClient) -> None:
    resp = await http_client.get("/api/v1/catalog/999999")
    assert resp.status_code == 404


async def test_attempt_on_nonexistent_test(http_client: httpx.AsyncClient) -> None:
    tok = await _register_and_login(http_client)
    resp = await http_client.post("/api/v1/attempts/", json={"test_id": 999999}, headers=_auth(tok))
    assert resp.status_code == 404

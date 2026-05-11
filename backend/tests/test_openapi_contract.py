"""
Basic OpenAPI contract checks for client generation.
"""

from app.main import app


def test_openapi_contains_error_response_schema():
    schema = app.openapi()
    components = schema.get("components", {})
    schemas = components.get("schemas", {})
    assert "ErrorResponse" in schemas


def test_openapi_operations_have_standard_error_responses():
    schema = app.openapi()
    paths = schema.get("paths", {})
    # Pick a stable operation
    op = paths["/api/v1/auth/me"]["get"]
    responses = op.get("responses", {})
    assert "401" in responses
    assert "application/json" in responses["401"]["content"]
    ref = responses["401"]["content"]["application/json"]["schema"]["$ref"]
    assert ref == "#/components/schemas/ErrorResponse"


def test_openapi_progress_endpoints_are_typed():
    schema = app.openapi()
    paths = schema.get("paths", {})

    op = paths["/api/v1/statistics/me/progress"]["get"]
    resp = op["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    assert resp == "#/components/schemas/StudentProgressResponse"

    op = paths["/api/v1/statistics/classroom/{classroom_id}/progress"]["get"]
    resp = op["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    assert resp == "#/components/schemas/ClassroomProgressResponse"


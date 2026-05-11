"""
OpenAPI schema patching for better client generation.

Goals:
- Make error envelope discoverable for code generators.
- Add standard error responses to operations.
"""

import copy
import typing as tp

import fastapi
from fastapi.openapi import utils as openapi_utils

from app.schemas import errors as error_schemas


def _error_schema() -> dict[str, tp.Any]:
    return error_schemas.ErrorResponse.model_json_schema(
        ref_template="#/components/schemas/{model}",
        mode="validation",
    )


def _inject_components(schema: dict[str, tp.Any]) -> None:
    components = schema.setdefault("components", {})
    schemas = components.setdefault("schemas", {})

    # Ensure ErrorResponse exists in components.
    error_component_name = "ErrorResponse"
    if error_component_name not in schemas:
        # model_json_schema contains definitions nested; extract the main schema and defs.
        error_schema = _error_schema()
        defs = error_schema.pop("$defs", {})
        # Merge defs first (if any).
        for name, definition in defs.items():
            schemas.setdefault(name, definition)
        schemas[error_component_name] = error_schema


def _error_ref() -> dict[str, tp.Any]:
    return {"$ref": "#/components/schemas/ErrorResponse"}


def _ensure_error_responses(schema: dict[str, tp.Any]) -> None:
    paths = schema.get("paths", {})
    for _path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        for _method, operation in methods.items():
            if not isinstance(operation, dict):
                continue
            responses = operation.setdefault("responses", {})

            for status_code, description in (
                ("400", "Bad Request"),
                ("401", "Unauthorized"),
                ("403", "Forbidden"),
                ("404", "Not Found"),
                ("409", "Conflict"),
                ("422", "Validation Error"),
                ("500", "Internal Server Error"),
            ):
                if status_code in responses:
                    # Keep existing if explicitly documented.
                    continue
                responses[status_code] = {
                    "description": description,
                    "content": {"application/json": {"schema": _error_ref()}},
                }


def install_openapi_patch(app: fastapi.FastAPI) -> None:
    """
    Override app.openapi() to return patched schema.
    """

    def custom_openapi() -> dict[str, tp.Any]:
        if app.openapi_schema is not None:
            return tp.cast(dict[str, tp.Any], app.openapi_schema)

        base = openapi_utils.get_openapi(
            title=app.title,
            version=app.version,
            routes=app.routes,
            description=app.description,
        )
        schema = copy.deepcopy(base)
        _inject_components(schema)
        _ensure_error_responses(schema)
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi


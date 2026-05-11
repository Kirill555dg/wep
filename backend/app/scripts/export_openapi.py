"""
Export OpenAPI schema to a JSON file.

Usage:
  python -m app.scripts.export_openapi --out ../frontend/src/shared/api/openapi.json
"""

import argparse
import json
import pathlib

from app.main import app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="Output path for openapi.json")
    args = parser.parse_args()

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    schema = app.openapi()
    out_path.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()


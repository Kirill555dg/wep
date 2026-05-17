#!/bin/bash
set -euo pipefail

NAME="health-checker"
DIST="$(dirname "$0")/dist"

cd "$(dirname "$0")"

# Build standalone binary via PyInstaller in a clean venv
uv venv .build-venv > /dev/null
source .build-venv/bin/activate
uv pip install --quiet -r requirements.txt pyinstaller
pyinstaller --onefile --name "$NAME" __main__.py
deactivate
rm -rf .build-venv __pycache__/ "$NAME".spec build/

echo "Binary: $DIST/$NAME"

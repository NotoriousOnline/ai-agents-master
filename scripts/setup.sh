#!/usr/bin/env bash
# AI Agents Master — Python environment setup (macOS/Linux)
# Run from repo root: ./scripts/setup.sh
# Requires: Python 3.11+ (python3.11, python3, or pyenv)

set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PYTHON_VERSION="3.11"
if [[ -f .python-version ]]; then
  PYTHON_VERSION=$(cat .python-version | tr -d '\n')
fi

echo "Using Python $PYTHON_VERSION (edit .python-version to change)"

# Prefer pyenv if available
if command -v pyenv &>/dev/null; then
  export PYENV_VERSION="$PYTHON_VERSION"
  PYTHON_CMD="pyenv exec python"
elif command -v "python${PYTHON_VERSION}" &>/dev/null; then
  PYTHON_CMD="python${PYTHON_VERSION}"
elif command -v python3 &>/dev/null; then
  PYTHON_CMD="python3"
else
  echo "Python 3.11+ not found. Install from https://www.python.org/downloads/ or use pyenv."
  exit 1
fi

# Check version
VER=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || true)
if [[ -z "$VER" ]] || [[ "$VER" < "3.11" ]]; then
  echo "Need Python 3.11+. Got: $($PYTHON_CMD --version 2>&1)"
  exit 1
fi

echo "Creating virtual environment in .venv ..."
if [[ -d .venv ]]; then
  echo ".venv already exists; skipping creation."
else
  $PYTHON_CMD -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip -q
[[ -f requirements.txt ]] && pip install -r requirements.txt -q
pip install -e . -q

echo "Done. Activate with: source .venv/bin/activate"
echo "Run API: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

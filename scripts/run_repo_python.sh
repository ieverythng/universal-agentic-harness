#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_OVERRIDE="${UAH_PYTHON_BIN:-}"

if [[ -n "${PYTHON_OVERRIDE}" && -x "${PYTHON_OVERRIDE}" ]]; then
  PYTHON_BIN="${PYTHON_OVERRIDE}"
elif [[ -x "${REPO_ROOT}/.venv/bin/python" ]]; then
  PYTHON_BIN="${REPO_ROOT}/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
else
  echo "Unable to resolve Python. Set UAH_PYTHON_BIN or create .venv." >&2
  exit 1
fi

cd "${REPO_ROOT}"
exec "${PYTHON_BIN}" "$@"

#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required to create the development environment." >&2
  exit 1
fi

if [[ ! -x ".venv/bin/python" ]]; then
  python3 -m venv .venv
fi

.venv/bin/python -m pip install -e ".[test]" -r requirements-dev.txt
.venv/bin/python -m pre_commit install --install-hooks --hook-type pre-commit
.venv/bin/python -m pre_commit install --hook-type pre-push

echo "Development tools are ready."
echo "Run ./scripts/run_precommit.sh before committing or pushing."

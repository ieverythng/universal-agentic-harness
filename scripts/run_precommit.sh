#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

if [[ ! -x ".venv/bin/python" ]]; then
  echo "Missing .venv. Run ./scripts/setup_dev_tools.sh first." >&2
  exit 1
fi

.venv/bin/python -m pre_commit run --all-files
.venv/bin/python scripts/precommit_cache.py record

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

HOOKS_DIR="$(git rev-parse --git-path hooks)"
if [[ "${HOOKS_DIR}" != /* ]]; then
  HOOKS_DIR="${REPO_ROOT}/${HOOKS_DIR}"
fi
PRE_PUSH_HOOK="${HOOKS_DIR}/pre-push"
PRE_PUSH_DELEGATE="${PRE_PUSH_HOOK}.pre-commit"

if [[ -f "${PRE_PUSH_HOOK}" ]] && grep -Fq "UAH pre-push guard" "${PRE_PUSH_HOOK}"; then
  if [[ ! -x "${PRE_PUSH_DELEGATE}" ]]; then
    echo "The UAH pre-push guard has no executable pre-commit delegate." >&2
    exit 1
  fi
else
  if [[ -e "${PRE_PUSH_DELEGATE}" ]]; then
    echo "Refusing to replace existing ${PRE_PUSH_DELEGATE}." >&2
    exit 1
  fi
  .venv/bin/python -m pre_commit install --hook-type pre-push
  if [[ ! -x "${PRE_PUSH_HOOK}" ]]; then
    echo "pre-commit did not install ${PRE_PUSH_HOOK}." >&2
    exit 1
  fi
  mv "${PRE_PUSH_HOOK}" "${PRE_PUSH_DELEGATE}"
fi

install -m 755 "${REPO_ROOT}/scripts/pre_push_guard.sh" "${PRE_PUSH_HOOK}"

echo "Development tools are ready."
echo "Run ./scripts/run_precommit.sh before committing or pushing."

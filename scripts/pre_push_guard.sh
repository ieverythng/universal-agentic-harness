#!/usr/bin/env bash
# UAH pre-push guard: validate every Git ref update before pre-commit runs.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "${REPO_ROOT}"

HOOKS_DIR="$(git rev-parse --git-path hooks)"
if [[ "${HOOKS_DIR}" != /* ]]; then
  HOOKS_DIR="${REPO_ROOT}/${HOOKS_DIR}"
fi
PRE_COMMIT_DELEGATE="${HOOKS_DIR}/pre-push.pre-commit"
if [[ ! -x "${PRE_COMMIT_DELEGATE}" ]]; then
  echo "The pre-commit pre-push delegate is missing; run ./scripts/setup_dev_tools.sh." >&2
  exit 1
fi
if [[ ! -x "${REPO_ROOT}/.venv/bin/python" ]]; then
  echo "Missing .venv. Run ./scripts/setup_dev_tools.sh first." >&2
  exit 1
fi

PUSH_INPUT="$(mktemp "${TMPDIR:-/tmp}/uah-pre-push.XXXXXX")"
cleanup() {
  rm -f "${PUSH_INPUT}"
}
trap cleanup EXIT
cat > "${PUSH_INPUT}"

(
  unset UAH_PYTHON_BIN SKIP PYTHONPATH
  "${REPO_ROOT}/.venv/bin/python" -I \
    "${REPO_ROOT}/scripts/precommit_cache.py" check --push-input "${PUSH_INPUT}"
)

if (
  unset UAH_PYTHON_BIN SKIP PYTHONPATH
  "${PRE_COMMIT_DELEGATE}" "$@" < "${PUSH_INPUT}"
); then
  status=0
else
  status=$?
fi
rm -f "${PUSH_INPUT}"
trap - EXIT
exit "${status}"

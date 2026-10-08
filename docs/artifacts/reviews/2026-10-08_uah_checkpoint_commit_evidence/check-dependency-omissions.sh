#!/bin/bash
set -u
candidate=/tmp/uah-checkpoint02/candidate
base=/tmp/uah-pilot-review-before
cd "$candidate" || exit 2
export PYTHONPATH=src
export UAH_PYTHON_BIN=/home/juanbeck/universal-agentic-harness/.venv/bin/python
mkdir -p /tmp/uah-checkpoint02/omissions
for path in \
  src/ab_harness/prompt_compiler.py \
  src/ab_harness/runtime_controls.py \
  src/ab_harness/task_ingress_authority.py \
  src/ab_harness/environment_ingress.py \
  src/ab_harness/proposal_admission.py \
  src/ab_harness/domain_lifecycle.py \
  src/ab_harness/environment.py \
  src/ab_harness_nao/qualification.py \
  src/ab_harness_nao/smoke.py
do
  name=$(basename "$path" .py)
  saved=/tmp/uah-checkpoint02/omissions/$name.current
  cp "$path" "$saved"
  if [ -f "$base/$path" ]; then
    cp "$base/$path" "$path"
  else
    rm "$path"
  fi
  timeout 45s "$UAH_PYTHON_BIN" -m pytest -q > "/tmp/uah-checkpoint02/omissions/$name.log" 2>&1
  result=$?
  cp "$saved" "$path"
  printf '%s\t%s\n' "$path" "$result"
done

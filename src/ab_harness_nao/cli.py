"""Command-line entry point for the recorded NAO adapter canary."""

from __future__ import annotations

import json
from collections.abc import Sequence

from ab_harness_nao.smoke import run_smoke


def main(argv: Sequence[str] | None = None) -> int:
    del argv
    report = run_smoke()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report['status'] == 'passed' else 1

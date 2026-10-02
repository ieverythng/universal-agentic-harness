#!/usr/bin/env python3
"""Render or verify the committed O1 recorded-canary Observatory example."""

from __future__ import annotations

import argparse
from pathlib import Path

from ab_harness.observatory import render_observatory
from ab_harness_nao.smoke import record_smoke_run


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "artifacts" / "observatory" / "o1_recorded_nao_canary.html"
TITLE = "UAH Observatory O1: Recorded NAO Canary"


def expected_html() -> str:
    recorded = record_smoke_run()
    return render_observatory(
        recorded.lifecycle_ledger,
        title=TITLE,
    ).html


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail when the committed example differs from the recorded canary",
    )
    args = parser.parse_args()
    rendered = expected_html()
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("committed O1 Observatory example is stale")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

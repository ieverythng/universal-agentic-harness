"""Command-line entry point for portable UAH qualification."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from ab_harness.smoke import run_smoke


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog='ab_harness')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser(
        'smoke',
        help='run accepted, rejected, and Workbench canaries without ROS',
    )
    args = parser.parse_args(argv)

    if args.command == 'smoke':
        report = run_smoke()
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report['status'] == 'passed' else 1
    return 2

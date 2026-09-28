#!/usr/bin/env python3
"""Render the canonical Agentic Harness Markdown files with the shared web theme."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "scripts" / "render_markdown_html.py"
DOCS = (
    Path("plans/universal_agentic_harness_masterplan"),
    Path("plans/universal_agentic_harness_development_log"),
    Path("plans/domain_initialization_and_ab_coupling"),
    Path("architecture/universal_agentic_harness_foundation"),
    Path("architecture/neural_workbench_adaptive_ab_harness"),
    Path("architecture/observatory_contract"),
    Path("artifacts/decisions/2026-08-04_uah_h2_neural_workbench_grill"),
    Path("artifacts/decisions/2026-09-08_uah_identity_environment_and_memory_grill"),
    Path("artifacts/reviews/2026-08-17_uah_h2_commit_review"),
    Path("gtm/investor_handoff/README"),
    Path("gtm/investor_handoff/executive_brief"),
    Path("gtm/investor_handoff/technical_diligence"),
    Path("gtm/investor_handoff/gtm_and_investment_case"),
)
LEGACY_REDIRECTS = {
    "universal_agentic_harness_masterplan": "../plans/universal_agentic_harness_masterplan.html",
    "universal_agentic_harness_development_log": "../plans/universal_agentic_harness_development_log.html",
    "universal_agentic_harness_foundation": "../architecture/universal_agentic_harness_foundation.html",
    "neural_workbench_adaptive_ab_harness": "../architecture/neural_workbench_adaptive_ab_harness.html",
}
REDIRECT_TEMPLATE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8" />
<meta http-equiv="refresh" content="0; url={target}" />
<link rel="canonical" href="{target}" />
<title>Document moved</title></head>
<body><p>This document moved to <a href="{target}">{target}</a>.</p></body></html>
"""


def theme_links(html_path: Path) -> str:
    assets = os.path.relpath(ROOT / "docs" / "assets", html_path.parent)
    assets = assets.replace("\\", "/")
    return (
        f'  <link rel="stylesheet" href="{assets}/harness-theme.css" />\n'
        f'  <script defer src="{assets}/harness-theme.js"></script>\n'
    )


def rendered_html(relative_path: Path) -> str:
    markdown_path = ROOT / "docs" / relative_path.with_suffix(".md")
    html_path = ROOT / "docs" / relative_path.with_suffix(".html")
    with tempfile.TemporaryDirectory() as temporary_directory:
        temporary_path = Path(temporary_directory) / "rendered.html"
        subprocess.run(
            [sys.executable, str(RENDERER), str(markdown_path), str(temporary_path)],
            check=True,
        )
        html = temporary_path.read_text(encoding="utf-8")
    return html.replace("</head>", theme_links(html_path) + "</head>")


def render(relative_path: Path, *, check: bool) -> bool:
    html_path = ROOT / "docs" / relative_path.with_suffix(".html")
    expected = rendered_html(relative_path)
    if check:
        return html_path.exists() and html_path.read_text(encoding="utf-8") == expected
    html_path.write_text(expected, encoding="utf-8")
    return True


def render_legacy_redirects(*, check: bool) -> tuple[Path, ...]:
    legacy_dir = ROOT / "docs" / "agentic_harness"
    if not check:
        legacy_dir.mkdir(parents=True, exist_ok=True)
    drifted: list[Path] = []
    for name, target in LEGACY_REDIRECTS.items():
        path = legacy_dir / f"{name}.html"
        expected = REDIRECT_TEMPLATE.format(target=target)
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                drifted.append(path)
        else:
            path.write_text(expected, encoding="utf-8")
    return tuple(drifted)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    drifted: list[Path] = []
    for name in DOCS:
        if not render(name, check=args.check):
            drifted.append(ROOT / "docs" / name.with_suffix(".html"))
    drifted.extend(render_legacy_redirects(check=args.check))
    if drifted:
        print("Generated documentation is out of sync:", file=sys.stderr)
        for path in drifted:
            print(f"  {path.relative_to(ROOT)}", file=sys.stderr)
        print("Run python scripts/render_agentic_harness_docs.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

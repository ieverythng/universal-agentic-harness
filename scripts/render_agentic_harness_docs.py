#!/usr/bin/env python3
"""Render the canonical Agentic Harness Markdown files with the shared web theme."""

from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys


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
    Path("artifacts/reviews/2026-08-17_uah_h2_commit_review"),
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


def render(relative_path: Path) -> None:
    markdown_path = ROOT / "docs" / relative_path.with_suffix(".md")
    html_path = ROOT / "docs" / relative_path.with_suffix(".html")
    subprocess.run(
        [sys.executable, str(RENDERER), str(markdown_path), str(html_path)],
        check=True,
    )
    html = html_path.read_text(encoding="utf-8")
    html_path.write_text(
        html.replace("</head>", theme_links(html_path) + "</head>"),
        encoding="utf-8",
    )


def render_legacy_redirects() -> None:
    legacy_dir = ROOT / "docs" / "agentic_harness"
    legacy_dir.mkdir(parents=True, exist_ok=True)
    for name, target in LEGACY_REDIRECTS.items():
        (legacy_dir / f"{name}.html").write_text(
            REDIRECT_TEMPLATE.format(target=target),
            encoding="utf-8",
        )


def main() -> int:
    for name in DOCS:
        render(name)
    render_legacy_redirects()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

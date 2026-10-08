"""Read-only predeclared controls for frozen consolidation Markdown inputs."""

from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[4]
BEFORE = ROOT / "docs/artifacts/reviews/2026-10-08_uah_consolidation_evidence/before"
INPUTS = [
    (BEFORE / "universal_agentic_harness_masterplan.md.txt", ROOT / "docs/plans"),
    (BEFORE / "universal_agentic_harness_development_log.md.txt", ROOT / "docs/plans"),
    (ROOT / "docs/plans/universal_agentic_harness_masterplan.md", ROOT / "docs/plans"),
    (ROOT / "docs/plans/universal_agentic_harness_development_log.md", ROOT / "docs/plans"),
    (
        ROOT / "docs/artifacts/reviews/2026-10-08_uah_consolidated_handoff.md",
        ROOT / "docs/artifacts/reviews",
    ),
]
failed = False
for path, canonical_parent in INPUTS:
    content = path.read_text()
    missing = []
    checked = 0
    for match in re.finditer(r"!?\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)", content):
        target = match.group(1).strip("<>")
        parts = urlsplit(target)
        if parts.scheme or parts.netloc or not parts.path:
            continue
        candidate = canonical_parent / unquote(parts.path)
        checked += 1
        if not candidate.exists():
            line = content[: match.start()].count("\n") + 1
            missing.append((line, target))
    whitespace = [
        number
        for number, line in enumerate(content.splitlines(), 1)
        if line.rstrip(" \t") != line and not line.endswith("  ")
    ]
    newline_ok = content.endswith("\n") and not content.endswith("\n\n")
    failed |= bool(missing or whitespace or not newline_ok)
    print(
        f"{path.relative_to(ROOT)}: local_links={checked}; "
        f"missing={missing}; trailing_whitespace={whitespace}; "
        f"terminal_newline={newline_ok}"
    )
raise SystemExit(int(failed))

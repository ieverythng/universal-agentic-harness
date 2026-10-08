"""Read-only, local-link control for the consolidation's before/after inputs."""

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        self.ids.update([values["id"]] if "id" in values else [])
        for field in ("href", "src"):
            if field in values:
                self.targets.append(values[field])


ROOT = Path(__file__).resolve().parents[3]
BEFORE = Path("/tmp/uah-consolidation-second.RSzTwF")
NAMES = [
    "docs/plans/universal_agentic_harness_masterplan",
    "docs/plans/universal_agentic_harness_development_log",
]
HANDOFF = "docs/artifacts/reviews/2026-10-08_uah_consolidated_handoff.md"
results = []
for state, root in (("before", BEFORE), ("after", ROOT)):
    paths = [root / (name + suffix) for name in NAMES for suffix in (".md", ".html")]
    if state == "after":
        paths.append(root / HANDOFF)
    for path in paths:
        body = path.read_text()
        if path.suffix == ".html":
            parser = Links()
            parser.feed(body)
            targets = parser.targets
        else:
            targets = re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", body)
        local = []
        failures = []
        for target in targets:
            uri = urlsplit(target)
            if uri.scheme or uri.netloc:
                continue
            resolved = (path.parent / unquote(uri.path)).resolve() if uri.path else path
            local.append(target)
            if not resolved.exists():
                failures.append({"target": target, "reason": "missing file"})
            elif uri.fragment and resolved.suffix == ".html":
                dest = Links()
                dest.feed(resolved.read_text())
                if unquote(uri.fragment) not in dest.ids:
                    failures.append({"target": target, "reason": "missing HTML anchor"})
        results.append({"state": state, "path": str(path.relative_to(root)),
                        "local_links": len(local), "failures": failures})
print(json.dumps(results, indent=2))
raise SystemExit(any(row["failures"] for row in results))

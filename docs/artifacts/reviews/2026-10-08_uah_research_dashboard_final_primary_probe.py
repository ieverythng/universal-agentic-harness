"""Independent public-CLI probes; source and review receipts are not imported."""

import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


REPO = Path(__file__).resolve().parents[3]
CURRENT = REPO / "scripts/render_research_dashboard.py"
BEFORE = REPO / "docs/artifacts/reviews/2026-10-08_uah_research_dashboard_final_evidence/render_research_dashboard.py.before"
START = "<!-- research-records:start -->"
END = "<!-- research-records:end -->"
BASE = "# Independent dashboard\n\nReconciled: 2026-10-07. Scope: navigation.\n\n## Catalog\n\n" + START + "\n" + END + "\n"


class Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self.table = None
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.table = {"header": [], "rows": []}
            self.tables.append(self.table)
        elif tag == "tr" and self.table is not None:
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = [tag, ""]

    def handle_data(self, data):
        if self.cell is not None:
            self.cell[1] += data

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None:
            self.row.append(self.cell)
            self.cell = None
        elif tag == "tr" and self.row is not None:
            if self.row and self.row[0][0] == "th":
                self.table["header"] = [item[1] for item in self.row]
            else:
                self.table["rows"].append([item[1] for item in self.row])
            self.row = None
        elif tag == "table":
            self.table = None


def filters(page):
    tables = Tables()
    tables.feed(page)
    script = re.findall(r"<script>(.*?)</script>", page, re.S)[-1]
    program = r"""
const fs = require('fs');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const buttons = ['all', 'investigation', 'proposed_experiment', 'executed_probe', 'reviewed_outcome', 'h_series_dependency'].map(kind => ({dataset: {kind}, events: {}, addEventListener(n, cb) {this.events[n] = cb}, setAttribute() {}}));
const tableList = input.tables.map(t => ({querySelector() {return {textContent:t.header[0]}}, rows:t.rows.map(c => ({hidden:false, textContent:c.join(' '), querySelectorAll() {return c.map(textContent=>({textContent}))}})), querySelectorAll(){return this.rows}}));
const tabs = {querySelectorAll(){return buttons}};
const search = {value:'', addEventListener(n, cb){this[n] = cb}};
const gate = {value:'all', addEventListener(n, cb){this[n] = cb}};
const count = {textContent:''};
const document = {querySelectorAll(){return tableList}, getElementById(id){return {'research-tabs':tabs, 'research-search':search, 'research-gate':gate, 'research-count':count}[id]}};
eval(input.script);
let out = [['all',count.textContent]];
for (const b of buttons.slice(1)) {b.events.click();out.push([b.dataset.kind,count.textContent]);}
buttons[0].events.click();gate.value='H3';gate.change();out.push(['H3',count.textContent]);
gate.value='all';search.value='candidate';search.input();out.push(['candidate',count.textContent]);
search.value='does not exist';search.input();out.push(['no-match',count.textContent]);
console.log(JSON.stringify(out));
"""
    result = subprocess.run(["node", "-e", program], input=json.dumps({"tables": tables.tables, "script": script}), text=True, capture_output=True)
    return {"rc": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}


CASES = {
    "ordinary": BASE,
    "empty-records": BASE,
    "two-records": BASE,
    "two-records-reversed": BASE,
    "history-section": BASE.replace("## Catalog", "## Historical prose\n\nReconciled: 2024-02-29.\n\n## Catalog"),
    "history-tab-heading": BASE.replace("## Catalog", "##\tHistorical prose\n\nReconciled: 2024-02-29.\n\n## Catalog"),
    "history-indented-heading": BASE.replace("## Catalog", "  ## Historical prose\n\nReconciled: 2024-02-29.\n\n## Catalog"),
    "history-nbsp-heading": BASE.replace("## Catalog", "##\u00a0Historical prose\n\nReconciled: 2024-02-29.\n\n## Catalog"),
    "fenced-history": BASE.replace("## Catalog", "```text\nReconciled: 2024-02-29.\n&#35; &#60; &#39; &amp;\n```\n\n## Catalog"),
    "indented-fenced-history": BASE.replace("## Catalog", "    ```text\nReconciled: 2024-02-29.\n    ```\n\n## Catalog"),
    "tilde-history": BASE.replace("## Catalog", "~~~text\nReconciled: 2024-02-29.\n&#35; &#60;\n~~~\n\n## Catalog"),
    "trailing-authored-entities": BASE + "\n## Historical prose\n\nReconciled: 2024-02-29.\n\n```text\n&#35; &#60; &#39; &amp;\n```\n",
    "missing-top": BASE.replace("Reconciled: 2026-10-07. Scope: navigation.\n", ""),
    "repeated-top": BASE.replace("Reconciled: 2026-10-07. Scope: navigation.", "Reconciled: 2026-10-07.\nReconciled: 2026-10-07."),
    "malformed-top": BASE.replace("2026-10-07. Scope: navigation.", "2026-10-07T13:00:00+02:00."),
    "invalid-leap-day": BASE.replace("2026-10-07. Scope: navigation.", "2025-02-29."),
    "missing-end": BASE.replace(END, ""),
    "repeated-start": BASE + START,
    "reverse-markers": BASE.replace(START + "\n" + END, END + "\n" + START),
    "spaced-start": BASE.replace(START, "<!--  research-records:start -->"),
}


def run_case(script, text, name):
    with tempfile.TemporaryDirectory(prefix="uah-final-independent-") as temporary:
        root = Path(temporary)
        source = root / "docs/source.md"
        source.parent.mkdir()
        source.write_text("Proposal only. No observed effect.\n")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        registry = {"schema_version": 1, "reconciled_at": "2026-10-08", "records": [{"id": "candidate", "title": "Candidate <img src=x onerror=alert(1)> # ' &amp; [link](javascript:x) | * _ ` \\ \u2028next\vlast", "summary": "Proposal &#35; & <svg onload=alert(1)> [link](javascript:x)", "kind": "proposed_experiment", "date": "2026-10-08", "h_series_dependencies": ["H3"], "source": {"path": "docs/source.md", "sha256": digest}, "references": []}]}
        if name == "empty-records":
            registry["records"] = []
        elif name.startswith("two-records"):
            registry["records"].append({**registry["records"][0], "id": "dependency", "title": "Unknown dependency date", "kind": "h_series_dependency", "date": None, "h_series_dependencies": ["H1"], "source": {"path": "docs/source.md", "sha256": None}})
            if name.endswith("reversed"):
                registry["records"].reverse()
        registry_path = root / "registry.json"
        registry_path.write_text(json.dumps(registry))
        markdown = root / "docs/dashboard.md"
        markdown.write_text(text)
        args = [sys.executable, str(script), "--repo-root", str(root), "--registry", str(registry_path), "--markdown", str(markdown), "--as-of", "2026-10-08"]
        env = {**os.environ, "PYTHONPATH": str(REPO / "scripts")}
        result = subprocess.run(args, env=env, text=True, capture_output=True)
        actual = markdown.read_text()
        out = {"rc": result.returncode, "stderr": result.stderr.strip(), "source_unchanged": hashlib.sha256(source.read_bytes()).hexdigest() == digest, "markdown_unchanged_on_error": actual == text if result.returncode else None, "html_absent_on_error": not markdown.with_suffix(".html").exists() if result.returncode else None}
        if result.returncode:
            check = subprocess.run(args + ["--check"], env=env, text=True, capture_output=True)
            out.update({"check_rc": check.returncode, "check_stderr": check.stderr.strip(), "unchanged_after_error_check": markdown.read_text() == text})
        if not result.returncode:
            page = markdown.with_suffix(".html").read_text()
            expected_before = text.split(START)[0].replace("Reconciled: 2026-10-07.", "Reconciled: 2026-10-08.", 1)
            out["outside_generated_region_preserved"] = actual.split(START)[0] == expected_before and actual.split(END)[1] == text.split(END)[1]
            out.update({"authored_history_preserved": "Reconciled: 2024-02-29." in actual if "Reconciled: 2024-02-29." in text else None, "history_h2_present": "<h2>Historical prose</h2>" in page if "Historical prose" in text else None, "literal_entities_preserved": "&amp;#35; &amp;#60; &amp;#39; &amp;amp;" in page if "&#35; &#60; &#39; &amp;" in text else None, "active_metadata_html_absent": '<img src=' not in page and '<svg onload=' not in page and 'href="javascript:' not in page, "td_count": page.count("<td>"), "controls": page.count('id="research-tabs"')})
            check = subprocess.run(args + ["--check"], env=env, text=True, capture_output=True)
            rerender = subprocess.run(args, env=env, text=True, capture_output=True)
            out.update({"check_rc": check.returncode, "repeat_rc": rerender.returncode, "idempotent_html": page == markdown.with_suffix(".html").read_text(), "idempotent_md": actual == markdown.read_text()})
            if name in {"ordinary", "empty-records", "two-records", "two-records-reversed"}:
                out["actual_script_filters"] = filters(page)
        return out


def replay_real_catalog(script):
    registry_path = REPO / "docs/research/experiment_registry.json"
    registry = json.loads(registry_path.read_text())
    evidence = BEFORE.parent
    with tempfile.TemporaryDirectory(prefix="uah-final-real-catalog-") as temporary:
        root = Path(temporary)
        paths = {"docs/research/experiment_registry.json"}
        for entry in registry["records"]:
            paths.add(entry["source"]["path"])
            paths.update(entry["references"])
        for path in paths:
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / path, target)
        markdown = root / "docs/research/uah_research_dashboard.md"
        shutil.copyfile(evidence / "uah_research_dashboard.md.before", markdown)
        shutil.copyfile(evidence / "uah_research_dashboard.html.before", markdown.with_suffix(".html"))
        args = [sys.executable, str(script), "--repo-root", str(root), "--as-of", "2026-10-08"]
        env = {**os.environ, "PYTHONPATH": str(REPO / "scripts")}
        before_md = markdown.read_bytes()
        before_html = markdown.with_suffix(".html").read_bytes()
        before_sources = {path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in paths}
        initial = subprocess.run(args + ["--check"], env=env, capture_output=True, text=True)
        render = subprocess.run(args, env=env, capture_output=True, text=True)
        check = subprocess.run(args + ["--check"], env=env, capture_output=True, text=True)
        repeat = subprocess.run(args, env=env, capture_output=True, text=True)
        return {"initial_check_rc": initial.returncode, "render_rc": render.returncode, "check_rc": check.returncode, "repeat_rc": repeat.returncode, "md_matches_exact_snapshot": markdown.read_bytes() == before_md, "html_matches_exact_snapshot": markdown.with_suffix(".html").read_bytes() == before_html, "sources_and_registry_unchanged": before_sources == {path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in paths}, "filters": filters(markdown.with_suffix(".html").read_text())}


if __name__ == "__main__":
    print(json.dumps({"real_catalog": {"current": replay_real_catalog(CURRENT), "exact_before": replay_real_catalog(BEFORE)}}, ensure_ascii=False))
    for name, text in CASES.items():
        print(json.dumps({"case": name, "current": run_case(CURRENT, text, name), "exact_before": run_case(BEFORE, text, name)}, ensure_ascii=False))

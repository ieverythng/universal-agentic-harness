from pathlib import Path

from scripts import render_agentic_harness_docs
from scripts.render_markdown_html import render_markdown
from scripts.render_agentic_harness_docs import LEGACY_REDIRECTS
from scripts.render_agentic_harness_docs import ROOT


def test_marked_uah_flowchart_renders_as_accessible_inline_svg():
    markdown = '''# Architecture

```mermaid
%% uah-render: Admission and evidence
flowchart TB
    Proposal["Typed Proposal"]:::proposal
    Gate["Semantic Admission"]:::gate
    Evidence["Owner Evidence"]:::evidence
    Proposal --> Gate
    Gate -->|admitted| Evidence
```
'''

    _, body = render_markdown(markdown)

    assert '<svg' in body
    assert 'aria-label="Admission and evidence"' in body
    assert 'Typed Proposal' in body
    assert 'Semantic Admission' in body
    assert 'Owner Evidence' in body
    assert 'language-mermaid' not in body


def test_unmarked_mermaid_flowchart_remains_readable_source():
    markdown = '''# Architecture

```mermaid
flowchart TB
    A["Source"] --> B["Target"]
```
'''

    _, body = render_markdown(markdown)

    assert 'class="language-mermaid"' in body
    assert 'flowchart TB' in body


def test_legacy_agentic_harness_pages_only_redirect_to_canonical_docs():
    legacy_dir = ROOT / "docs" / "agentic_harness"

    for name, target in LEGACY_REDIRECTS.items():
        redirect = (legacy_dir / f"{name}.html").read_text(encoding="utf-8")

        assert f'http-equiv="refresh" content="0; url={target}"' in redirect
        assert f'<link rel="canonical" href="{target}"' in redirect
        assert not (legacy_dir / f"{name}.md").exists()


def test_check_mode_reports_drift_without_rewriting_generated_html(
    monkeypatch, tmp_path, capsys
):
    generated = tmp_path / "docs" / "plans" / "sample.html"
    generated.parent.mkdir(parents=True)
    generated.write_text("stale", encoding="utf-8")
    monkeypatch.setattr(render_agentic_harness_docs, "ROOT", tmp_path)
    monkeypatch.setattr(
        render_agentic_harness_docs, "DOCS", (Path("plans/sample"),)
    )
    monkeypatch.setattr(render_agentic_harness_docs, "LEGACY_REDIRECTS", {})
    monkeypatch.setattr(
        render_agentic_harness_docs,
        "rendered_html",
        lambda _relative_path: "expected",
    )

    result = render_agentic_harness_docs.main(["--check"])

    assert result == 1
    assert generated.read_text(encoding="utf-8") == "stale"
    assert "docs/plans/sample.html" in capsys.readouterr().err

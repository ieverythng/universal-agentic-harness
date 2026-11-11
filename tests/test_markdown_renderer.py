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


def _tracker_markdown(items):
    import json

    fence = chr(96) * 3
    block = {
        "snapshot_date": "2026-11-03",
        "snapshot_note": "Static snapshot.",
        "items": items,
    }
    return "# Plan\n\n## Delivery\n\n" + fence + "uah-tracker\n" + json.dumps(block) + "\n" + fence + "\n"


def _tracker_item(**overrides):
    item = {
        "id": "SPR-01",
        "title": "Example",
        "kind": "sprint",
        "repo": "UAH",
        "state": "Draft",
        "summary": "Planning only.",
        "details": [{"label": "Gate", "value": "H0-H1"}],
    }
    return {**item, **overrides}


def test_uah_tracker_renders_static_cards_escapes_text_and_hides_controls():
    from scripts.render_markdown_html import render_markdown

    item = _tracker_item(title="Ingress <script>alert(1)</script>")
    _, body = render_markdown(_tracker_markdown([item]))

    assert body.count('class="tracker-card"') == 1
    assert 'class="tracker-controls" hidden' in body
    assert 'data-kind="sprint"' in body
    assert 'data-status="draft"' in body
    assert "Ingress &lt;script&gt;alert(1)&lt;/script&gt;" in body
    assert "<script>alert(1)</script>" not in body
    assert '<article class="tracker-card" hidden' not in body


def test_uah_tracker_supports_all_four_statuses():
    from scripts.render_markdown_html import render_markdown

    states = ("Draft", "Open", "Ready for review", "Closed")
    items = [
        _tracker_item(id=f"ITEM-{index}", state=state)
        for index, state in enumerate(states)
    ]
    _, body = render_markdown(_tracker_markdown(items))

    for state in states:
        assert f'data-status="{state.lower()}"' in body
        assert f">{state}</option>" in body


def test_uah_tracker_rejects_duplicate_ids_unsupported_states_and_untrusted_urls():
    import pytest

    from scripts.render_markdown_html import render_markdown

    item = _tracker_item()
    with pytest.raises(ValueError, match="duplicate"):
        render_markdown(_tracker_markdown([item, item]))

    with pytest.raises(ValueError, match="unsupported state"):
        render_markdown(_tracker_markdown([_tracker_item(state="Merged")]))

    with pytest.raises(ValueError, match="trusted GitHub host"):
        render_markdown(
            _tracker_markdown([_tracker_item(url="javascript:alert(1)")])
        )


def test_masterplan_has_pr_cards_ten_sprints_crosswalk_and_scoped_assets():
    import json

    from scripts.render_markdown_html import render_markdown

    markdown_path = ROOT / "docs" / "plans" / "universal_agentic_harness_masterplan.md"
    markdown = markdown_path.read_text(encoding="utf-8")
    fence = chr(96) * 3 + "uah-tracker\n"
    block = markdown.split(fence, maxsplit=1)[1].split(chr(96) * 3, maxsplit=1)[0]
    data = json.loads(block)
    records = data["items"]

    assert [record["id"] for record in records] == [
        "PR #1",
        "PR2 branch",
        *[f"SPR-{number:02d}" for number in range(1, 11)],
    ]
    assert records[0]["state"] == "Closed"
    assert records[0]["url"].endswith("/pull/1")
    assert records[1]["state"] == "Open"
    assert any(
        detail["label"] == "GitHub PR state"
        and detail["value"] == "No PR opened"
        for detail in records[1]["details"]
    )
    sprints = records[2:]
    assert all(record["state"] == "Draft" for record in sprints)
    assert "blocked on predecessors" in data["snapshot_note"]
    assert "unauthorized for execution" in data["snapshot_note"]

    spr08 = next(record for record in sprints if record["id"] == "SPR-08")
    assert "adfcb269" in str(spr08["details"])
    spr10 = next(record for record in sprints if record["id"] == "SPR-10")
    assert "separate planning repository" in str(spr10["details"])
    assert "ae4a0eef" in str(spr10["details"])
    assert "Neural-Wokbench" in str(spr10["details"])
    assert "codex/sprint-10-wb-base" in str(spr10["details"])
    assert "/home/" not in str(records)
    assert "/Users/" not in str(records)

    for workpackage in (
        "H0-C1",
        "H0-C2",
        "H0-C3",
        "H0-C4",
        "H0-C5",
        "H1-R1",
        "H1-R2",
        "H1-R3",
        "H2-P1",
        "H2-P2",
        "H2-P3",
    ):
        assert workpackage in markdown

    _, body = render_markdown(markdown)
    assert body.count('class="tracker-card"') == 12
    assert '12 records</p>' in body
    assert '12 delivery records</p>' not in body
    assert '<label>Delivery status<select' in body
    assert 'Observed GitHub PR state and H-gate qualification are separate facts.' in body
    assert "PR #1" in body
    assert "No PR opened" in body

    rendered = render_agentic_harness_docs.rendered_html(
        Path("plans/universal_agentic_harness_masterplan")
    )
    assert "masterplan-tracker.css" in rendered
    assert "masterplan-tracker.js" in rendered

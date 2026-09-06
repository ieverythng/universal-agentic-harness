from scripts.render_markdown_html import render_markdown


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

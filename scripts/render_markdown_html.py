#!/usr/bin/env python3
"""Render Markdown into lightweight standalone HTML without external deps."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import html
import re
from pathlib import Path


def _escape(text: str) -> str:
    return html.escape(text, quote=True)


def _inline(text: str) -> str:
    escaped = _escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    return escaped


def _is_table_row(line: str) -> bool:
    return line.count("|") >= 2 and line.strip().startswith("|") and line.strip().endswith("|")


def _is_table_divider(line: str) -> bool:
    stripped = line.strip()
    if not _is_table_row(stripped):
        return False
    core = stripped.strip("|").replace(" ", "")
    return bool(core) and all(ch in "-:|" for ch in core)


def _table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _starts_block(line: str) -> bool:
    stripped = line.strip()
    return bool(
        not stripped
        or stripped.startswith("```")
        or re.match(r"^#{1,6}\s+", stripped)
        or stripped in ("---", "***")
        or stripped.startswith("> ")
        or re.match(r"^[-*]\s+", stripped)
        or re.match(r"^\d+\.\s+", stripped)
        or _is_table_row(stripped)
    )


def _wrapped_list_text(lines: list[str], start: int, initial: str) -> tuple[str, int]:
    parts = [initial.strip()]
    index = start + 1
    while index < len(lines):
        raw = lines[index]
        if not raw[:1].isspace() or _starts_block(raw):
            break
        parts.append(raw.strip())
        index += 1
    return " ".join(parts), index


def _render_mermaid(code_text: str) -> str:
    stripped = code_text.strip()
    if stripped.startswith("sequenceDiagram"):
        return _runtime_sequence_svg()
    rendered = _render_marked_uah_flowchart(code_text)
    if rendered is not None:
        return rendered
    escaped = _escape(code_text)
    return (
        '<div class="diagram"><pre><code '
        'class="language-mermaid">%s</code></pre></div>' % escaped
    )


@dataclass(frozen=True)
class _FlowNode:
    node_id: str
    label: str
    kind: str


@dataclass(frozen=True)
class _FlowEdge:
    source: str
    target: str
    label: str
    kind: str


def _render_marked_uah_flowchart(code_text: str) -> str | None:
    lines = [line.strip() for line in code_text.splitlines() if line.strip()]
    if not lines or not lines[0].startswith("%% uah-render:"):
        return None

    title = lines[0].split(":", 1)[1].strip()
    if len(lines) < 2:
        return None
    flow = re.fullmatch(r"flowchart\s+(TB|LR)", lines[1])
    if flow is None:
        return None

    nodes: dict[str, _FlowNode] = {}
    edges: list[_FlowEdge] = []
    node_pattern = re.compile(
        r'^([A-Za-z][\w-]*)\["([^"]+)"\](?:(?:[:]){3}([\w-]+))?$'
    )
    edge_pattern = re.compile(
        r"^([A-Za-z][\w-]*)\s+(-->|-\.->|==>)\s*"
        r"(?:\|([^|]+)\|\s*)?([A-Za-z][\w-]*)$"
    )
    for line in lines[2:]:
        node_match = node_pattern.fullmatch(line)
        if node_match:
            node_id, label, kind = node_match.groups()
            nodes[node_id] = _FlowNode(node_id, label, kind or "default")
            continue
        edge_match = edge_pattern.fullmatch(line)
        if edge_match:
            source, kind, label, target = edge_match.groups()
            edges.append(_FlowEdge(source, target, label or "", kind))
            continue
        if line.startswith(("class ", "classDef ")):
            continue
        return None

    if not nodes or any(edge.source not in nodes or edge.target not in nodes for edge in edges):
        return None

    levels = _flow_levels(tuple(nodes), edges)
    positions, width, height = _flow_positions(tuple(nodes), levels, flow.group(1))
    palette = {
        "identity": ("#e8edff", "#5268d8"),
        "semantic": ("#e5f5f2", "#168778"),
        "projection": ("#e8f2ff", "#2879c7"),
        "compiler": ("#e9f6e7", "#3d8b4e"),
        "model": ("#f0eaff", "#7657b8"),
        "proposal": ("#f5ecff", "#8b5bb7"),
        "gate": ("#efe6ff", "#6c4ca5"),
        "domain": ("#fff0e2", "#cb6d26"),
        "execution": ("#ffe7e5", "#bf5048"),
        "evidence": ("#fff6cf", "#b18416"),
        "trace": ("#e5f4f4", "#247e83"),
        "observatory": ("#e8edf2", "#536475"),
        "default": ("#f4f5f7", "#626a73"),
    }

    edge_svg = []
    for edge in edges:
        x1, y1 = positions[edge.source]
        x2, y2 = positions[edge.target]
        if flow.group(1) == "TB":
            start = (x1, y1 + 38)
            end = (x2, y2 - 38)
            middle = (start[1] + end[1]) / 2
            path = (
                f"M {start[0]:.1f} {start[1]:.1f} "
                f"C {start[0]:.1f} {middle:.1f}, {end[0]:.1f} {middle:.1f}, "
                f"{end[0]:.1f} {end[1]:.1f}"
            )
        else:
            start = (x1 + 112, y1)
            end = (x2 - 112, y2)
            middle = (start[0] + end[0]) / 2
            path = (
                f"M {start[0]:.1f} {start[1]:.1f} "
                f"C {middle:.1f} {start[1]:.1f}, {middle:.1f} {end[1]:.1f}, "
                f"{end[0]:.1f} {end[1]:.1f}"
            )
        dash = ' stroke-dasharray="8 7"' if edge.kind == "-.->" else ""
        stroke_width = "3" if edge.kind == "==>" else "2"
        edge_svg.append(
            f'<path d="{path}" fill="none" stroke="#9aa8bd" '
            f'stroke-width="{stroke_width}"{dash} marker-end="url(#uah-arrow)" />'
        )
        if edge.label:
            label_x = (start[0] + end[0]) / 2
            label_y = (start[1] + end[1]) / 2 - 7
            label_width = max(78, len(edge.label) * 7 + 18)
            edge_svg.append(
                f'<rect x="{label_x - label_width / 2:.1f}" y="{label_y - 15:.1f}" '
                f'width="{label_width}" height="22" rx="8" fill="#172033" />'
            )
            edge_svg.append(
                f'<text x="{label_x:.1f}" y="{label_y:.1f}" text-anchor="middle" '
                f'font-size="13" fill="#dce6f7">{_escape(edge.label)}</text>'
            )

    node_svg = []
    for node_id, node in nodes.items():
        x, y = positions[node_id]
        fill, stroke = palette.get(node.kind, palette["default"])
        node_svg.append(
            f'<rect x="{x - 112:.1f}" y="{y - 38:.1f}" width="224" height="76" '
            f'rx="15" fill="{fill}" stroke="{stroke}" stroke-width="2" />'
        )
        node_svg.append(_flow_node_text(node.label, x, y))

    return f'''<div class="diagram uah-flow-diagram">
  <svg viewBox="0 0 {width} {height}" role="img" aria-label="{_escape(title)}">
    <defs>
      <marker id="uah-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#9aa8bd"></path>
      </marker>
    </defs>
    <g font-family="Inter, Liberation Sans, Arial, sans-serif">{"".join(edge_svg)}{"".join(node_svg)}</g>
  </svg>
  <div class="caption">{_escape(title)}</div>
</div>'''


def _flow_levels(node_ids: tuple[str, ...], edges: list[_FlowEdge]) -> dict[str, int]:
    levels = {node_id: 0 for node_id in node_ids}
    for _ in node_ids:
        changed = False
        for edge in edges:
            candidate = levels[edge.source] + 1
            if candidate > levels[edge.target]:
                levels[edge.target] = candidate
                changed = True
        if not changed:
            break
    return levels


def _flow_positions(
    node_ids: tuple[str, ...],
    levels: dict[str, int],
    direction: str,
) -> tuple[dict[str, tuple[float, float]], int, int]:
    grouped: dict[int, list[str]] = {}
    for node_id in node_ids:
        grouped.setdefault(levels[node_id], []).append(node_id)
    max_level = max(grouped)
    max_count = max(len(items) for items in grouped.values())
    positions: dict[str, tuple[float, float]] = {}

    if direction == "TB":
        width = max(1040, max_count * 270 + 80)
        height = max(260, (max_level + 1) * 138 + 70)
        for level, items in grouped.items():
            spacing = width / (len(items) + 1)
            for index, node_id in enumerate(items, start=1):
                positions[node_id] = (spacing * index, 68 + level * 138)
        return positions, width, height

    width = max(900, (max_level + 1) * 290 + 80)
    height = max(360, max_count * 112 + 80)
    for level, items in grouped.items():
        spacing = height / (len(items) + 1)
        for index, node_id in enumerate(items, start=1):
            positions[node_id] = (145 + level * 290, spacing * index)
    return positions, width, height


def _flow_node_text(label: str, x: float, y: float) -> str:
    parts = [part.strip() for part in re.split(r"<br\s*/?>", label) if part.strip()]
    if not parts:
        parts = [label]
    longest = max(len(part) for part in parts)
    font_size = 12 if longest > 28 else 13 if longest > 23 else 15
    start_y = y - ((len(parts) - 1) * 9)
    spans = []
    for index, part in enumerate(parts):
        weight = "700" if index == 0 else "500"
        spans.append(
            f'<tspan x="{x:.1f}" y="{start_y + index * 20:.1f}" '
            f'font-weight="{weight}">{_escape(part)}</tspan>'
        )
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
        f'font-size="{font_size}" fill="#172033">{"".join(spans)}</text>'
    )


def _runtime_sequence_svg() -> str:
    labels = [
        ("User", 80),
        ("chatbot_llm", 270),
        ("nao_orchestrator", 490),
        ("planner_llm", 710),
        ("AB=1 Skills", 900),
        ("KB + Scene", 1080),
        ("dialogue\nmanager", 1238),
    ]
    lifelines = [80, 270, 490, 710, 900, 1080, 1280]
    messages = [
        (80, 270, 78, "natural language request"),
        (270, 1080, 110, "query KB rows + scene summary"),
        (270, 270, 142, "project compact grounded_context"),
        (270, 490, 174, "/nao_orchestrator/planner_request"),
        (490, 490, 206, "PlannerGate admission"),
        (490, 710, 238, "/planner/request"),
        (710, 710, 270, "prompt + validation"),
        (710, 490, 302, "/intents"),
        (490, 900, 334, "dispatch executable steps"),
        (900, 1080, 366, "requery live evidence"),
        (900, 490, 398, "typed skill result"),
        (490, 710, 430, "/planner/execution_feedback"),
        (710, 490, 462, "/planner/dialogue_act when needed"),
        (490, 1280, 494, "/nao_orchestrator/planner_dialogue_act"),
        (1280, 80, 526, "spoken response"),
    ]
    label_svg = "\n".join(
        _svg_multiline_text(label, x, 26)
        for label, x in labels
    )
    lifeline_svg = "\n".join(
        '<line x1="%d" y1="42" x2="%d" y2="560"></line>' % (x, x)
        for x in lifelines
    )
    message_svg = []
    for x1, x2, y, text in messages:
        marker = 'url(#arr)' if x2 >= x1 else 'url(#arr-left)'
        message_svg.append(
            '<line x1="%d" y1="%d" x2="%d" y2="%d" marker-end="%s"></line>'
            % (x1, y, x2, y, marker)
        )
        text_x = min(x1, x2) + abs(x2 - x1) / 2
        message_svg.append(
            '<text x="%.1f" y="%d" text-anchor="middle">%s</text>'
            % (text_x, y - 7, _escape(text))
        )
    return """
<div class="diagram">
  <svg viewBox="0 0 1360 590" role="img" aria-label="Runtime sequence diagram">
    <defs>
      <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#111"></path>
      </marker>
      <marker id="arr-left" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="6" markerHeight="6" orient="auto">
        <path d="M 10 0 L 0 5 L 10 10 z" fill="#111"></path>
      </marker>
    </defs>
    <g class="diagram-labels">%s</g>
    <g class="lifelines">%s</g>
    <g class="messages">%s</g>
  </svg>
  <div class="caption">Figure 1. Runtime message and responsibility sequence.</div>
</div>
""" % (label_svg, lifeline_svg, "\n".join(message_svg))


def _svg_multiline_text(label: str, x: int, y: int) -> str:
    parts = str(label).split("\n")
    if len(parts) == 1:
        return '<text x="%s" y="%s" text-anchor="middle">%s</text>' % (
            x,
            y + 6,
            _escape(parts[0]),
        )
    tspans = []
    for index, part in enumerate(parts):
        dy = 0 if index == 0 else 24
        tspans.append(
            '<tspan x="%s" dy="%s">%s</tspan>' % (x, dy, _escape(part))
        )
    return '<text x="%s" y="%s" text-anchor="middle">%s</text>' % (
        x,
        y,
        "".join(tspans),
    )


def render_markdown(markdown_text: str) -> tuple[str, str]:
    lines = markdown_text.splitlines()
    output: list[str] = []
    title = "Document"

    in_code = False
    code_lang = ""
    code_lines: list[str] = []

    in_ul = False
    in_ol = False
    in_blockquote = False

    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip("\n")
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code:
                raw_code_text = "\n".join(code_lines)
                if code_lang == "mermaid":
                    output.append(_render_mermaid(raw_code_text))
                else:
                    code_text = _escape(raw_code_text)
                    cls = f' class="language-{_escape(code_lang)}"' if code_lang else ""
                    output.append(f"<pre><code{cls}>{code_text}</code></pre>")
                in_code = False
                code_lang = ""
                code_lines = []
            else:
                in_code = True
                code_lang = stripped[3:].strip()
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        if not stripped:
            if in_ul:
                output.append("</ul>")
                in_ul = False
            if in_ol:
                output.append("</ol>")
                in_ol = False
            if in_blockquote:
                output.append("</blockquote>")
                in_blockquote = False
            i += 1
            continue

        if _is_table_row(stripped):
            table_lines = [stripped]
            j = i + 1
            while j < len(lines) and _is_table_row(lines[j].strip()):
                table_lines.append(lines[j].strip())
                j += 1
            if len(table_lines) >= 2 and _is_table_divider(table_lines[1]):
                if in_ul:
                    output.append("</ul>")
                    in_ul = False
                if in_ol:
                    output.append("</ol>")
                    in_ol = False
                if in_blockquote:
                    output.append("</blockquote>")
                    in_blockquote = False
                header = _table_cells(table_lines[0])
                output.append("<table><thead><tr>")
                for cell in header:
                    output.append(f"<th>{_inline(cell)}</th>")
                output.append("</tr></thead><tbody>")
                for row in table_lines[2:]:
                    output.append("<tr>")
                    for cell in _table_cells(row):
                        output.append(f"<td>{_inline(cell)}</td>")
                    output.append("</tr>")
                output.append("</tbody></table>")
                i = j
                continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            level = len(heading.group(1))
            text = heading.group(2).strip()
            if title == "Document" and level == 1:
                title = text
            if in_ul:
                output.append("</ul>")
                in_ul = False
            if in_ol:
                output.append("</ol>")
                in_ol = False
            if in_blockquote:
                output.append("</blockquote>")
                in_blockquote = False
            output.append(f"<h{level}>{_inline(text)}</h{level}>")
            i += 1
            continue

        if stripped in ("---", "***"):
            if in_ul:
                output.append("</ul>")
                in_ul = False
            if in_ol:
                output.append("</ol>")
                in_ol = False
            if in_blockquote:
                output.append("</blockquote>")
                in_blockquote = False
            output.append("<hr />")
            i += 1
            continue

        if stripped.startswith("> "):
            if in_ul:
                output.append("</ul>")
                in_ul = False
            if in_ol:
                output.append("</ol>")
                in_ol = False
            if not in_blockquote:
                output.append("<blockquote>")
                in_blockquote = True
            output.append(f"<p>{_inline(stripped[2:])}</p>")
            i += 1
            continue
        if in_blockquote:
            output.append("</blockquote>")
            in_blockquote = False

        unordered = re.match(r"^[-*]\s+(.+)$", stripped)
        if unordered:
            if in_ol:
                output.append("</ol>")
                in_ol = False
            if not in_ul:
                output.append("<ul>")
                in_ul = True
            item_text, next_index = _wrapped_list_text(lines, i, unordered.group(1))
            output.append(f"<li>{_inline(item_text)}</li>")
            i = next_index
            continue

        ordered = re.match(r"^\d+\.\s+(.+)$", stripped)
        if ordered:
            if in_ul:
                output.append("</ul>")
                in_ul = False
            if not in_ol:
                output.append("<ol>")
                in_ol = True
            item_text, next_index = _wrapped_list_text(lines, i, ordered.group(1))
            output.append(f"<li>{_inline(item_text)}</li>")
            i = next_index
            continue

        if in_ul:
            output.append("</ul>")
            in_ul = False
        if in_ol:
            output.append("</ol>")
            in_ol = False

        paragraph = [stripped]
        i += 1
        while i < len(lines) and not _starts_block(lines[i]):
            paragraph.append(lines[i].strip())
            i += 1
        output.append(f"<p>{_inline(' '.join(paragraph))}</p>")

    if in_code:
        raw_code_text = "\n".join(code_lines)
        if code_lang == "mermaid":
            output.append(_render_mermaid(raw_code_text))
        else:
            code_text = _escape(raw_code_text)
            cls = f' class="language-{_escape(code_lang)}"' if code_lang else ""
            output.append(f"<pre><code{cls}>{code_text}</code></pre>")
    if in_ul:
        output.append("</ul>")
    if in_ol:
        output.append("</ol>")
    if in_blockquote:
        output.append("</blockquote>")

    return title, "\n".join(output)


def _title_page(title: str) -> str:
    escaped_title = _escape(title)
    if "planner" not in title.lower() and "grounding" not in title.lower():
        return ""
    if "end-to-end" in title.lower() or "supervisor walkthrough" in title.lower():
        heading = (
            "Technical Memory Draft Baseline<br/>"
            "End-to-End Planner Dialogue Flow"
        )
        scope = "Runtime flow, JSON contracts, replanning lineage, and dialogue relay behavior."
        metadata_rows = [
            '<tr><td>Document type:</td><td>Architecture and contract walkthrough</td></tr>',
            '<tr><td>Academic year:</td><td>2025-2026</td></tr>',
            '<tr><td>Date:</td><td>2026-06-01</td></tr>',
        ]
    else:
        heading = escaped_title
        scope = "Grounding ownership, compact context projection, and planner/skill evidence seams."
        metadata_rows = [
            '<tr><td>Document type:</td><td>Architecture and contract walkthrough</td></tr>',
            '<tr><td>Academic year:</td><td>2025-2026</td></tr>',
        ]
    metadata_rows.extend(
        [
            '<tr><td>Scope:</td><td>%s</td></tr>' % _escape(scope),
            (
                '<tr><td>Repository:</td><td><span class="small">'
                'https://github.com/ieverythng/nao-ros4hri-bridge'
                '</span></td></tr>'
            ),
        ]
    )
    metadata_html = "\n        ".join(metadata_rows)
    return f"""
    <section class="title-page">
      <div class="title-top">
        <h2>Universitat Autonoma de Barcelona</h2>
        <p>Master Degree in Modelling for Science and Engineering</p>
        <p>Institution / Lab: IIIA-CSIC</p>
        <h1>{heading}</h1>
        <p>Formal architecture and contract section for technical review.</p>
      </div>
      <table class="title-meta">
        {metadata_html}
      </table>
    </section>
"""


def build_html(title: str, body: str) -> str:
    page_title = _escape(title)
    title_page = _title_page(title)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{page_title}</title>
  <style>
    @page {{
      size: A4;
      margin: 2.6cm 2.2cm 2.4cm 2.2cm;
    }}
    :root {{
      --ink: #111;
      --muted: #3a3a3a;
      --line: #1f1f1f;
      --soft: #f3f3f3;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: #fff;
      font-family: "Liberation Serif", "Times New Roman", Times, serif;
      font-size: 11.5pt;
      line-height: 1.42;
    }}
    .doc {{
      max-width: 172mm;
      margin: 0 auto;
      padding: 0;
    }}
    .title-page {{
      min-height: 247mm;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      page-break-after: always;
    }}
    .title-top {{
      text-align: center;
      margin-top: 18mm;
    }}
    .title-top h1 {{
      font-size: 20pt;
      line-height: 1.28;
      margin: 20mm 0 8mm;
      font-weight: 700;
    }}
    .title-top h2 {{
      font-size: 13pt;
      margin: 0 0 3mm;
      font-weight: 600;
      border-bottom: 0;
    }}
    .title-top p {{
      margin: 2mm 0;
      color: var(--muted);
    }}
    .title-meta {{
      width: 100%;
      border-collapse: collapse;
      margin: 0 auto 20mm;
      font-size: 11pt;
    }}
    .title-meta td {{
      padding: 2.5mm 0;
      vertical-align: top;
      border: 0;
    }}
    .title-meta td:first-child {{
      width: 38mm;
      font-weight: 700;
    }}
    .small {{ font-size: 10.3pt; color: #222; }}
    h1, h2, h3 {{
      margin: 0 0 3mm;
      line-height: 1.28;
      font-weight: 700;
    }}
    h1 {{ font-size: 16.5pt; margin-top: 0; }}
    h2 {{
      font-size: 13pt;
      margin-top: 9mm;
      border-bottom: 0.5pt solid var(--line);
      padding-bottom: 1.5mm;
    }}
    h3 {{
      font-size: 11.8pt;
      margin-top: 6mm;
    }}
    p {{ margin: 2.2mm 0; }}
    ul, ol {{ margin: 2.5mm 0 2.5mm 6mm; padding: 0; }}
    li {{ margin: 1.4mm 0; }}
    pre {{
      margin: 2.5mm 0 4mm;
      background: var(--soft);
      border: 0.6pt solid #666;
      padding: 2.6mm 2.8mm;
      overflow-x: auto;
      white-space: pre;
      font-family: "Liberation Mono", "Courier New", monospace;
      font-size: 9.2pt;
      line-height: 1.3;
    }}
    code {{
      font-family: "Liberation Mono", "Courier New", monospace;
      background: #efefef;
      padding: 0.2mm 1mm;
      border: 0.4pt solid #d7d7d7;
      border-radius: 2px;
      font-size: 10.3pt;
    }}
    pre code {{
      background: transparent;
      padding: 0;
      border: 0;
      font-size: inherit;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 3mm 0 4mm;
      font-size: 10.8pt;
    }}
    th, td {{
      border: 0.6pt solid #333;
      padding: 2.2mm 2.3mm;
      vertical-align: top;
      overflow-wrap: anywhere;
      hyphens: auto;
    }}
    th {{
      background: #fafafa;
      text-align: left;
      font-weight: 700;
    }}
    .diagram {{
      margin: 4mm 0 5mm;
      border: 0.6pt solid #777;
      padding: 2mm;
      background: #fff;
    }}
    .diagram pre {{
      margin: 0;
      border: 0;
      background: #fcfcfc;
      font-size: 10.2pt;
      white-space: pre-wrap;
    }}
    .diagram svg {{
      width: 100%;
      height: auto;
      display: block;
    }}
    .diagram-labels {{
      font-family: "Liberation Serif", "Times New Roman", Times, serif;
      font-size: 25px;
      font-weight: 700;
      fill: #111;
    }}
    .lifelines {{
      stroke: #999;
      stroke-dasharray: 4 4;
    }}
    .messages {{
      stroke: #111;
      stroke-width: 1.35;
      fill: none;
    }}
    .messages text {{
      stroke: none;
      fill: #111;
      font-family: "Liberation Serif", "Times New Roman", Times, serif;
      font-size: 22px;
    }}
    .caption {{
      margin-top: 2mm;
      font-size: 10.5pt;
      color: #222;
      font-style: italic;
      text-align: center;
    }}
    blockquote {{
      border: 0.6pt solid #333;
      background: #fcfcfc;
      margin: 3mm 0;
      padding: 2.6mm 3mm;
      color: var(--muted);
    }}
    a {{ color: #111; }}
  </style>
</head>
<body>
  <main class="doc">
{title_page}
{body}
  </main>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="input markdown file")
    parser.add_argument("output", help="output html file")
    parser.add_argument("--title", default="", help="optional title override")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    markdown_text = input_path.read_text(encoding="utf-8")
    title, body = render_markdown(markdown_text)
    if args.title.strip():
        title = args.title.strip()
    output_path.write_text(build_html(title, body), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

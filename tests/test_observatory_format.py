"""O1 formatting remains hook-stable without changing raw event payloads."""

import html
import json

from ab_harness.observatory import render_observatory
from tests.test_observatory import _event


def test_empty_operation_graph_does_not_render_an_indented_blank_placeholder():
    event = _event(
        1, "task_started", trace_id="trace:format",
        data={"raw_text": "  leading\n \t \ntrailing  "},
    )
    original = event.to_dict()
    document = render_observatory((event,))

    assert not any(line and not line.strip() for line in document.html.split("\n"))
    expected_raw = html.escape(
        json.dumps(original, ensure_ascii=False, indent=2, sort_keys=True)
    )
    assert expected_raw in document.html
    assert document.projection.events[0].to_dict() == original
    graph = json.loads(document.graph_json)
    assert graph["nodes"][0]["id"] == event.event_id
    assert graph["nodes"][0]["event_type"] == "task_started"

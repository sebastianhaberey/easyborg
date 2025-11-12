import json
from collections.abc import Iterator
from typing import Any

import pytest
from easyborg.progress_parser import parse_progress


def _to_iterator(*events: dict[str, Any]) -> Iterator[str]:
    for e in events:
        yield json.dumps(e)


def test_parses_valid_progress_event():
    lines = _to_iterator(
        {
            "message": "50.0% Extracting: foo.txt",
            "current": 50,
            "total": 100,
            "msgid": "extract",
            "type": "progress_percent",
            "finished": False,
        }
    )

    result = list(parse_progress(lines))
    assert len(result) == 1
    event = result[0]
    assert event.total == 100
    assert event.current == 50


def test_skips_non_progress_events():
    lines = _to_iterator(
        {
            "message": "some other event",
            "current": 10,
            "total": 20,
            "msgid": "extract",
            "type": "foo",
        }
    )

    result = list(parse_progress(lines))
    assert result == []


def test_skips_progress_events_with_total_zero():
    # this occurs at the start of extract
    lines = _to_iterator(
        {
            "message": "Calculating total archive size for the progress indicator",
            "current": 0,
            "total": 0,
            "msgid": "extract",
            "type": "progress_percent",
        }
    )

    result = list(parse_progress(lines))
    assert result == []


def test_skips_finished_event():
    lines = _to_iterator(
        {
            "operation": 1,
            "msgid": "extract",
            "type": "progress_percent",
            "finished": True,
        }
    )

    result = list(parse_progress(lines))
    assert result == []


def test_handles_invalid_json():
    lines = iter(["not a JSON line"])
    with pytest.raises(RuntimeError, match=r"(?i)Unexpected event: 'not a JSON line'"):
        list(parse_progress(lines))

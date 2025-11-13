import json
from collections.abc import Generator, Iterator

from easyborg.model import ProgressEvent

CRITICAL_LEVELS = ["WARNING", "ERROR", "CRITICAL"]


def parse_progress(lines: Iterator[str]) -> Generator[ProgressEvent, None, None]:
    """
    Transform Borg extract JSON progress lines into progress events.
    """
    for line in lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            raise RuntimeError(f"Unexpected event: '{line}'")

        # print(f"{line}")

        event_type = event.get("type")

        if event_type == "log_message" and (event.get("levelname") in CRITICAL_LEVELS):
            raise RuntimeError(f"Received error event: {event.get('message')}")

        total = event.get("total")
        current = event.get("current")
        message = event.get("message")

        if total is None and current is None and message is None or message == "":
            continue

        yield ProgressEvent(total=total, current=current, message=message)

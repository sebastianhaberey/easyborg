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
            raise RuntimeError(f"{event.get('message')}")

        total = event.get("total")
        current = event.get("current")
        message = event.get("message")

        if not message:
            message = event.get("path")  # use path messages as a fallback

        if message:
            message = message.strip()

        if not total and not current and not message:
            continue

        yield ProgressEvent(total=total, current=current, message=message)

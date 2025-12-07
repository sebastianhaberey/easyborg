import sys
from pathlib import Path

import easyborg.cli
from easyborg import ui
from easyborg.cli import cli


def main():
    args = sys.argv[1:]
    if render_newlines(args):
        ui.newline()
    try:
        easyborg_executable = Path(sys.argv[0])
        cli.main(args, obj={"easyborg_executable": easyborg_executable})
    except Exception as e:
        if easyborg.cli.DEBUG_MODE:
            ui.stacktrace("Error while running easyborg")
        else:
            ui.exception(e)
    finally:
        if render_newlines(args):
            ui.newline()


def render_newlines(args: list[str]) -> bool:
    """Quick and dirty hack to evaluate if the two framing newlines should be rendered"""
    if "--headless" in args:
        return False  # don't output anything in headless mode to avoid system mails
    return True


if __name__ == "__main__":
    main()

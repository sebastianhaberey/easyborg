import sys
from pathlib import Path

import easyborg.cli
from easyborg import ui
from easyborg.cli import cli


def main():
    try:
        args = sys.argv[1:]
        easyborg_executable = Path(sys.argv[0])
        cli.main(args, obj={"easyborg_executable": easyborg_executable})
    except Exception as e:
        if easyborg.cli.DEBUG_MODE:
            ui.stacktrace("Error while running easyborg")
        else:
            ui.exception(e)
    finally:
        ui.newline()


if __name__ == "__main__":
    main()

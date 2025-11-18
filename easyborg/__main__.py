import sys
from pathlib import Path

import easyborg.cli
from easyborg import log_utils, ui
from easyborg.cli import cli

log_utils.disable_all_logging()  # disable logging until proper initialization (prevents duplicate UI output)


def main():
    ui.newline()
    try:
        args = sys.argv[1:]
        easyborg_executable = Path(sys.argv[0])
        cli.main(args, obj={"easyborg_executable": easyborg_executable})
    except Exception as e:
        if easyborg.cli.DEBUG_MODE:
            ui.exception("Error while running easyborg")
        else:
            ui.error(f"{e.__class__.__name__}:", str(e))
    finally:
        ui.newline()


if __name__ == "__main__":
    main()

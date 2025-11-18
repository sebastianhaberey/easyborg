import logging
import sys
from pathlib import Path

import easyborg.cli
from easyborg import ui
from easyborg.cli import cli
from rich.traceback import install

logger = logging.getLogger(__name__)


def main():
    install()

    ui.newline()

    try:
        args = sys.argv[1:]
        easyborg_executable = Path(sys.argv[0])
        cli(args, standalone_mode=False, obj={"easyborg_executable": easyborg_executable})
    except Exception as e:
        if logging.getLevelName(easyborg.cli.LOG_LEVEL) <= logging.DEBUG:
            logger.exception("❌ Error while running easyborg")
            raise e
        else:
            ui.error(f"{e.__class__.__name__}: {e}")

    ui.newline()


if __name__ == "__main__":
    main()

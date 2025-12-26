from easyborg import ui
from easyborg.fzf import Fzf
from easyborg.interaction import select_string
from easyborg.model import Context
from easyborg.util import open_path


class OpenCommand:
    def __init__(self, *, fzf: Fzf) -> None:
        self.fzf = fzf

    def run(self, context: Context) -> None:
        target = select_string(
            self.fzf,
            "Select item:",
            ["LOG FILE", "LOG DIR", "CONFIG FILE", "CONFIG DIR", "PYTHON DIR"],
        )
        if target is None:
            ui.abort()
            return

        ui.newline()

        if target == "LOG FILE":
            path = context.log_file
        elif target == "LOG DIR":
            path = context.log_dir
        elif target == "CONFIG FILE":
            path = context.config_file
        elif target == "CONFIG DIR":
            path = context.config_dir
        elif target == "PYTHON DIR":
            path = context.real_python_executable.parent
        else:
            raise RuntimeError(f"Unknown target {target}")

        try:
            open_path(path)
        except FileNotFoundError:
            ui.warn("Could not open file")
            return
        except RuntimeError:
            ui.warn("Not supported on your system")
            return

        ui.success("Open completed")

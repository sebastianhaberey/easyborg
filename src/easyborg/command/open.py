from easyborg import ui
from easyborg.model import Context
from easyborg.util import open_path


class OpenCommand:
    def __init__(self, *, context: Context) -> None:
        self.context = context

    def run(self, target: str) -> None:
        if target == "logfile":
            path = self.context.log_file
        elif target == "logdir":
            path = self.context.log_dir
        elif target == "configfile":
            path = self.context.config_file
        elif target == "configdir":
            path = self.context.config_dir
        else:
            ui.warn("Invalid target", target)
            return

        try:
            open_path(path)
        except FileNotFoundError:
            ui.warn("Could not open file")
        except RuntimeError:
            ui.warn("Not supported on your system")

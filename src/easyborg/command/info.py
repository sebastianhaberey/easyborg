from easyborg import ui
from easyborg.model import Config, Context
from easyborg.ui import link_path, render_dict


class InfoCommand:
    def __init__(self, *, config: Config) -> None:
        super().__init__()
        self.config = config

    def run(self, context: Context) -> None:
        """
        Display configuration details.
        """

        rows = [
            ("Configuration directory", link_path(context.config_dir)),
            ("Configuration file", link_path(context.config_file)),
            ("Log directory", link_path(context.log_dir) if context.log_dir else "not configured"),
            ("Log file", link_path(context.log_file) if context.log_file else "not configured"),
            ("Python executable", context.python_executable),
            ("Real python executable", context.real_python_executable),
            ("Real python directory", link_path(context.real_python_executable.parent)),
            ("Easyborg executable", context.easyborg_executable),
            ("Borg executable", context.borg_executable),
            ("fzf executable", context.fzf_executable),
        ]
        if context.expert:
            rows.extend(
                [
                    ("Expert mode", context.expert),
                    ("Debug mode", context.debug),
                    ("Profile", context.profile),
                ]
            )
        ui.header("Configuration", leading_newline=True)
        ui.table(rows, column_colors=(None, "bold cyan"))

        config = self.config

        if context.expert:
            ui.header("Environment")
            rows = [(key, value) for key, value in config.env.items()]
            ui.table(rows, headers=("Variable", "Value"), column_colors=(None, "bold cyan"))

        ui.header("Backup Folders")
        if config.backup_folders:
            rows = [(link_path(folder),) for folder in config.backup_folders]
            ui.table(rows, column_colors=("bold cyan",))
        else:
            ui.display("(no backup folders configured)", indent=1)

        repos = config.repos

        ui.header("Repositories")
        if repos:
            rows = [(repo.name, repo.url, repo.type.value) for repo in repos.values()]
            ui.table(
                rows,
                column_colors=(None, "bold cyan", "bold magenta"),
                headers=("Name", "URL", "Type"),
            )
        else:
            ui.display("(no repositories configured)", indent=1)

        if repos and context.expert:
            ui.header("Repository Environments")
            rows = [(repo.name, render_dict(repo.env, separator="\n")) for repo in repos.values()]
            ui.table(
                rows,
                headers=("Repository", "Environment"),
                column_colors=(None, None),
            )

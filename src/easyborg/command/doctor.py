from easyborg import ui
from easyborg.model import Config, Context
from easyborg.theme import StyleId, theme
from easyborg.ui import link_path, render_mapping

STYLES = theme().styles


class DoctorCommand:
    def __init__(self, *, config: Config) -> None:
        super().__init__()
        self.config = config

    def run(self, context: Context) -> None:
        rows = [
            ("Configuration dir", link_path(context.config_dir)),
            ("Configuration file", link_path(context.config_file)),
            ("Log dir", link_path(context.log_dir) if context.log_dir else "not configured"),
            ("Log file", link_path(context.log_file) if context.log_file else "not configured"),
            ("Python executable", context.python_executable),
            ("Real Python executable", context.real_python_executable),
            ("Real Python dir", link_path(context.real_python_executable.parent)),
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
        ui.header("Configuration", first=True)
        ui.table(
            rows,
            column_colors=(STYLES[StyleId.PRIMARY], None),
        )

        config = self.config

        if context.expert:
            ui.header("Environment")
            rows = [(key, value) for key, value in config.env.items()]
            ui.table(
                rows,
                column_colors=(STYLES[StyleId.PRIMARY], None),
            )

        ui.header("Backup Paths")
        if config.backup_paths:
            rows = [(link_path(path),) for path in config.backup_paths]
            ui.table(
                rows,
                column_colors=(STYLES[StyleId.PRIMARY], None),
            )
        else:
            ui.display("(no backup paths configured)", indent=1)

        repos = config.repos

        ui.header("Repositories")
        if repos:
            rows = [(repo.name, repo.url, repo.type.value) for repo in repos.values()]
            ui.table(
                rows,
                column_colors=(STYLES[StyleId.PRIMARY], None, STYLES[StyleId.SECONDARY]),
            )
        else:
            ui.display("(no repositories configured)", indent=1)

        if repos and context.expert:
            ui.header("Repository Environments")
            rows = [(repo.name, render_mapping(repo.env, separator="\n")) for repo in repos.values()]
            ui.table(
                rows,
                column_colors=(STYLES[StyleId.PRIMARY], None),
            )

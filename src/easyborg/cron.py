from pathlib import Path

from easyborg import ui
from easyborg.process import ProcessError, run_sync


class Cron:
    """
    Manage easyborg cron entries (macOS / Linux).

    Adds or removes entries in the user's crontab using the `crontab` CLI.
    """

    def __init__(self, profile: str):
        self.profile = profile
        self.marker = f"# easyborg:{profile}"

    def enable(
        self,
        command: str,
        easyborg_executable: Path,
        borg_executable: Path,
        fzf_executable: Path,
        *,
        schedule: str = "@hourly",
    ):
        """
        Add a cron entry with the given schedule (e.g. '@daily', '0 3 * * *').

        Idempotent: if there's already an entry for this profile, it will be replaced.
        """
        lines = _get_crontab()

        entry = (
            f"{schedule} "
            f"{easyborg_executable} "
            f"--profile {self.profile} "
            f"--headless "
            f"--borg-executable {borg_executable} "
            f"--fzf-executable {fzf_executable} "
            f"{command} "
            f"--tenacious "
            f"{self.marker}"
        )

        found = False
        if any(self.marker in line for line in lines):
            found = True
            lines = [line for line in lines if self.marker not in line]

        lines.append(entry)
        _write_crontab(lines)

        if found:
            ui.success("Updated easyborg cron entry", f'"{entry}"')
        else:
            ui.success("Added easyborg cron entry", f'"{entry}"')

    def disable(self):
        """
        Remove easyborg entry with current marker from the user's crontab.
        """
        existing = _get_crontab()
        if not any(self.marker in line for line in existing):
            ui.warn("No easyborg cron entries found")
            return

        updated = [line for line in existing if self.marker not in line]
        _write_crontab(updated)
        ui.success("Removed easyborg cron entry", f'profile "{self.profile}"')


def _get_crontab() -> list[str]:
    """Return current crontab lines, or an empty list if none."""
    try:
        lines = run_sync(["crontab", "-l"])
        if not lines or any("no crontab" in line.lower() for line in lines):
            return []
        return lines
    except ProcessError as e:
        # some systems exit non-zero when no crontab is set
        if e.stderr and "no crontab" in e.stderr.lower():
            return []
        raise RuntimeError("Could not read crontab") from e


def _write_crontab(lines: list[str]):
    run_sync(["crontab", "-"], cwd=None, input_lines=lines)

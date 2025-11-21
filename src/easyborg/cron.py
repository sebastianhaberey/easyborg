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

        Idempotent: if there's already an entry for this profile, no changes will be made.
        """
        existing = _get_crontab()

        if self.marker in existing:
            ui.warn("Easyborg cron entry already exists")
            return

        entry = (
            f"{schedule} "
            f"{easyborg_executable} "
            f"--profile {self.profile} "
            f"--scheduled "
            f"--borg-executable {borg_executable} "
            f"--fzf-executable {fzf_executable} "
            f"{command} "
            f"--tenacious "
            f"{self.marker}"
        )
        updated = _add_entry(existing, entry, self.marker)
        _write_crontab(updated)
        ui.success(f"Added easyborg cron entry: '{entry}'")

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
        ui.success("Removed easyborg cron entry")


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


def _add_entry(existing: list[str], entry: str, marker: str) -> list[str]:
    """Append the entry if not already present."""
    if any(marker in line for line in existing):
        # Replace existing easyborg lines for safety
        existing = [line for line in existing if marker not in line]
    existing.append(entry)
    return existing

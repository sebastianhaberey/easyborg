# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.11.0] - 2025-11-23

### Added

- New command "replace": replaces existing folders with restored folders

### Changed

- Big UI update
- Split Core class into dedicated command classes

## [0.10.1] - 2025-11-23

### Added

- Command "info" now also outputs REAL python executable and directory (useful for macOS system settings)
- UI status messages (success, warn, error) can now have a secondary text

### Changed

- Better error messages on missing dependencies

### Fixed

- Extremely early error output was swallowed
- Fixed missing dependencies (BorgBackup, fzf) on Homebrew package
- Hardened macOS GH workflow

## [0.10.0] - 2025-11-22

### Added

- Option for light mode (looks better on light terminals)
- Terminalizer config file for screen recordings
- Added environment variables EASYBORG_LIGHT_MODE, EASYBORG_PROFILE (expert), EASYBORG_DEBUG (expert)

### Changed

- BREAKING: "--scheduled" flag is now named "--headless" for clarity

## [0.9.6] - 2025-11-21

### Added

- Introduced "tenacious mode" for scheduled backups (keeps going even if one of the repositories fails)

### Fixed

- Fixed UI (highlighting, newlines)

## [0.9.5] - 2025-11-21

### Fixed

- Terminal output during scheduled runs would lead to system mails

## [0.9.4] - 2025-11-21

### Added

- Added Python executable path to info output

### Changed

- Trimmed progress messages to fit screen width

### Fixed

- Multiple paths on archive command did throw error
- macOS file attributes were not stripped for restore / extract

## [0.9.3] - 2025-11-21

### Added

- Snapshot selection dialogs show repository name for safety
- Added Github workflow to update Homebrew Formula
- Added Python script to generate Homebrew Formula from template

### Fixed

- Scheduled backup now runs under profile used during "easyborg enable"

## [0.9.2] - 2025-11-20

### Added

- Added Github workflow to automatically publish to PyPi

## [0.9.1] - 2025-11-20

### Changed

- UI finetuning
- Updated demo gifs
- Improved template file

## [0.9.0] - 2025-11-19

### Added

- Main command "backup": create snapshot of configured folders in backup repositories
- Main command "archive": create snapshot of specified folder in archive repositories (interactive)
- Main command "restore": restore snapshot to current working directory (interactive)
- Main command "extract": extract files / folders from snapshot (interactive)
- Main command "delete": delete snapshot from repository (interactive)
- Utility command "info": show info about the current configuration
- Utility command "enable": enable scheduled backups
- Utility command "disable": disable scheduled backups
- Help page
- Version page
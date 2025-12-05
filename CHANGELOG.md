# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.16.0] - 2025-12-02

## Added

- Homebrew bottles - faster and smaller install 

## Changed

- Running enable command will now update the existing schedule

## [0.15.2] - 2025-12-02

## Changed

- Updated fzf pointer

## Fixed

- Fixed slow installing process on homebrew

## [0.15.1] - 2025-12-01

## Changed 

- Removed fzf gutter symbol

## Fixed

- Fixed open command choices
- Fixed progress bar color in dark theme

## [0.15.0] - 2025-11-28

## Added

- Added backup short option -c for --comment

## Changed

- BREAKING: easyborg info is now easyborg doctor ("info" clashes with Borg info command)
- Streamlined UI symbols
- Source of truth in themes is now strings (enables future theme files)

## [0.14.1] - 2025-11-27

## Added

- Added test for replace command

## Changed

- Themes now contain the symbols used in the UI
- Changed theme names

## Fixed

- Fixed theme "ice_light"
- Fixed fzf query color in light themes

## [0.14.0] - 2025-11-26

## Added

- Introduced themes

## Fixed

- now checking backup paths are configured before backup, replace

## Removed

- BREAKING: removed option "--light-mode" (replaced by light themes)

## [0.13.0] - 2025-11-25

## Added

- Introduced short option "-p" for "--profiles"

## Changed

- BREAKING: Profiles are now in folder "profiles"
- BREAKING: Configuration option "backup_folders" is now "backup_paths" (can be either: file or folder)
- Updated documentation and help texts


## [0.12.0] - 2025-11-25

## Added

- Profiles are now a regular feature
- Open command: opens easyborg-related files (e.g. config) using system default application
- Added instructions for easyborg shell completion

## Fixed

- Fixed help width
- Fixed prompt color in light mode

## [0.11.2] - 2025-11-24

### Added

- Borg cheat sheet

### Changed

- UI: fixed newlines
- Confirmation now red in danger mode
- Updated documentation

## [0.11.1] - 2025-11-24

### Changed

- Fine tuned UI for more cohesive look

## [0.11.0] - 2025-11-23

### Added

- New command "replace": replaces existing paths with restored paths

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

- Main command "backup": create snapshot of configured paths in backup repositories
- Main command "archive": create snapshot of specified path in archive repositories (interactive)
- Main command "restore": restore snapshot to current working directory (interactive)
- Main command "extract": extract items from snapshot (interactive)
- Main command "delete": delete snapshot from repository (interactive)
- Utility command "info": show info about the current configuration
- Utility command "enable": enable scheduled backups
- Utility command "disable": disable scheduled backups
- Help page
- Version page
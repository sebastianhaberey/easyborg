# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.9.1] - 2025-11-19

### Changed

- various release-related changes

## [0.9.0] - 2025-11-19

### Added

- main command "backup": create snapshot of configured folders in backup repositories
- main command "archive": create snapshot of specified folder in archive repositories (interactive)
- main command "restore": restore snapshot to current working directory (interactive)
- main command "extract": extract files / folders from snapshot (interactive)
- main command "delete": delete snapshot from repository (interactive)
- utility command "info": show info about the current configuration
- utility command "enable": enable scheduled backups
- utility command "disable": disable scheduled backups
- help page
- version page
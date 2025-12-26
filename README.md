# Easyborg

Easyborg is a simple frontend for [BorgBackup](https://www.borgbackup.org/) (aka Borg)
with [fzf](https://github.com/junegunn/fzf) for user input.

[![Tests (Linux)](https://github.com/sebastianhaberey/easyborg/actions/workflows/tests-linux.yml/badge.svg)](https://github.com/sebastianhaberey/easyborg/actions/workflows/tests-linux.yml)
[![Tests (macOS)](https://github.com/sebastianhaberey/easyborg/actions/workflows/tests-macos.yml/badge.svg)](https://github.com/sebastianhaberey/easyborg/actions/workflows/tests-macos.yml)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/easyborg?label=Python)](https://pypi.org/project/easyborg/)
[![GitHub Release](https://img.shields.io/github/v/release/sebastianhaberey/easyborg?label=Release)](https://github.com/sebastianhaberey/easyborg/releases/)

## Features

* Fuzzy-search your snapshots lightning fast and extract the files you need
* Schedule hourly backups to run automatically in the background
* Backup / archive items to all configured repositories in one go
* Restore whole snapshots and replace the existing items on your local disk
* Easy-to-use UI

## Demonstration

### Extract

[![asciicast](https://asciinema.org/a/9jxikvvUgcDTnqaAtsKKovdJ5.svg)](https://asciinema.org/a/9jxikvvUgcDTnqaAtsKKovdJ5)

### Delete

[![asciicast](https://asciinema.org/a/BpnV3BoZv9FkUPlfACN3P0XPS.svg)](https://asciinema.org/a/BpnV3BoZv9FkUPlfACN3P0XPS)

## Setup

### Installation

You can choose between Homebrew / Linuxbrew or Python pipx.

#### Homebrew / Linuxbrew (recommended)

```
brew tap sebastianhaberey/easyborg
brew install easyborg
```

#### pipx

```
pipx install easyborg 
```

> **NOTE** You'll need a Python installation for pipx. Also make sure you
> have [BorgBackup](https://www.borgbackup.org/)
> and [fzf](https://github.com/junegunn/fzf) installed.

### Repositories

Easyborg doesn't provide any commands for creating repositories. It's easy to do with Borg, and you only have to do
it once. For Easyborg to access a repository, you must set up **BORG_PASSCOMMAND** or any other of the environment
variables Borg supports. If you succeed, you can access your repository without password prompt:

```
$ export BORG_PASSCOMMAND = "cat /Users/example/passphrase.txt"
$ borg list /Volumes/HD/backup
2025-11-13T17:46:47-F1AC35F6         Thu, 2025-11-13 17:46:47 [7b9fd68dd8e991ea9fd598ca015e10266498afc156969ccdfe67149124fd27cc]
2025-11-14T20:20:25-2965DCFB         Fri, 2025-11-14 20:20:25 [33539a1e5f2b83852cf5396ed442531d6b5d4cb2137522280285725c3ea5df48]
```

- If you're asked for a SSH password, set up access to your server via SSH key.
- If you're asked for a Borg repository
  password, [set up BORG_PASSCOMMAND](https://borgbackup.readthedocs.io/en/stable/usage/general.html#environment-variables).

> **NOTE** Be sure to _chmod 600_ your passphrase file to prevent others from accessing it.

Once that works, you can add the environment variable to Easyborg's configuration file (see below).

### Configuration

Minimal configuration example:

```
backup_paths = [
    "/Users/example/Documents",
]

[environment]
BORG_PASSCOMMAND = "cat /Users/example/passphrase.txt"

[repositories.BACKUP]
type = "backup"
url = "/Volumes/HD/backup"
```

Call _easyborg doctor_ to show the path to the configuration file:

```
$ easyborg doctor

Configuration:
  Configuration dir        /Users/example/Library/Application Support/easyborg/profiles/default
  Configuration file       /Users/example/Library/Application Support/easyborg/profiles/default/easyborg.toml
  Log dir                  /Users/example/Library/Logs/easyborg/default
  Log file                 /Users/example/Library/Logs/easyborg/default/easyborg.log
  
...
```

If you're on a modern terminal, you may be able to click on a path to open it (Ctrl + click on iTerm2).
Open the configuration file, keep and change the settings you like, delete those that you don't need. Verify your
settings by calling _easyborg doctor_ again.

## Usage

Easyborg currently supports _backup_, _archive_, _restore_, _extract_, _delete_, _replace_ and _autobackup_. Use

```
easyborg --help
```

for details on these commands and a few utility commands.

## Concept

Easyborg makes a distinction between _backup_ and _archive_.

|             | Purpose      | Data Type             | Data State | Trigger   | Retention        | 
|-------------|--------------|-----------------------|------------|-----------|------------------|
| **Backup**  | recovery     | needed for daily work | changing   | automatic | days to months   |
| **Archive** | preservation | needed for reference  | stable     | manual    | years to forever |

### Backup

If you enable automatic backups, Easyborg will create a snapshot of all configured paths in each configured
**backup repository** every full hour, i.e. at 12:00, 13:00 and so on. Then, snapshots are pruned to save space.
So after the 13:00 snapshot is written, the 12:00 snapshot will be deleted. A selection of snapshots will be
retained:

- Last snapshot of the day for seven days
- Last snapshot of the week for thirteen weeks

All other snapshots will be deleted.

> **NOTE** Pruning only occurs when _easyborg backup_ is called, manually or automatically.
> If you don't call it, your existing snapshots won't be touched.

### Archive

With Easyborg you create a snapshot in each configured **archive repository** whenever you want. For example if
you decide to tidy up your _Documents_ folder, a resonable strategy would be:

1. Delete all files you want to get rid of (especially big files)
2. Archive the remaining files using _easyborg archive_
3. Delete all files you want to keep but don't need for your daily work

That way, you start with a nice clean slate and still have all the documents you might need for later reference
stored away in your archive repositories. Of course you can follow a different approach. It's up to you what to archive
and when.

> **NOTE** Archive snapshots are never pruned automatically. If you want to delete an archive snapshot, use _easyborg
delete_.

## Restore / Replace

If you _back up_ or _archive_ an item, e.g.:

```
/Users/user/Documents
```

it will be stored in the snapshot as:

```
Users/user/Documents
```

When you _restore_ or _extract_ the item, it will be written into the current working directory:

```
<CWD>/Users/user/Documents
```

This is a safety feature. If you _do_ want to overwrite the original item, you can:

* Go to its parent folder (/ in the example) and run the restore action there (not recommended) **OR**
* Delete the original item and move the restored item in its place **OR**
* Use _easyborg replace_ which does that for you

### Glossary

| Easyborg           | Meaning                                                         | Borg             |
|--------------------|-----------------------------------------------------------------|------------------|
| Snapshot           | immutable point-in-time view of data                            | Archive          |
| Backup Repository  | storage of snapshots intended for recovery                      | Repository       |
| Archive Repository | storage of snapshots intended for preservation                  | Repository       |
| Snapshot Location  | Borg-style snapshot reference (`repository_url::snapshot_name`) | Archive Location |
| Repository URL     | Borg-style repository reference (local or remote)               | (same)           |
| backup (command)   | create snapshot in backup repository                            | `borg create`    |
| archive (command)  | create snapshot in archive repository                           | `borg create`    |
| extract (command)  | fetch selected items from snapshot                              | `borg extract`   | 
| restore (command)  | fetch entire snapshot                                           | `borg extract`   |

## Disclaimer

Even though I'm doing my best, and there's an automatic test suite that covers the critical functionality on Linux and
macOS, errors can happen. Use this application at your own risk. It is highly recommended to start with fresh
repositories to avoid data loss.

## Expert topics

If you're still here, have a look at the [expert topics](documentation/EXPERT.md)

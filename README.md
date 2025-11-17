# Easyborg

Easyborg is a simple frontend for the awesome [BorgBackup](https://www.borgbackup.org/) (aka Borg)
with [fzf](https://github.com/junegunn/fzf) for user input.

This project is currently WIP and cannot be used yet.

[![Tests (Linux)](https://github.com/sebastianhaberey/easyborg/actions/workflows/tests-linux.yml/badge.svg)](https://github.com/sebastianhaberey/easyborg/actions/workflows/tests-linux.yml)
[![Tests (macOS)](https://github.com/sebastianhaberey/easyborg/actions/workflows/tests-macos.yml/badge.svg)](https://github.com/sebastianhaberey/easyborg/actions/workflows/tests-macos.yml)

## Screenshots

### Extract

<img src="https://haberey.com/easyborg/extract-01.gif" width="1024"  alt="Extract command in terminal"/>

### Backup

<img src="https://haberey.com/easyborg/backup-01.gif" width="1024"  alt="Backup command in terminal"/>

## Setup

### Dependencies

Install:

- [BorgBackup](https://www.borgbackup.org/) (tested with v1.4.2)
- [fzf](https://github.com/junegunn/fzf) (tested with v0.66.1)

Verify:

```
$ borg --version
borg 1.4.2

$ fzf --version
0.66.1 (brew)
```

### Repositories

Easyborg doesn't provide any commands for creating repositories. It's easy to do with Borg, and you only have to do
it once. For Easyborg to access a repository, Borg commands must work on it **without** having to enter a password:

```
$ borg list /Volumes/STICK/backup
2025-11-13T17:46:47-F1AC35F6         Thu, 2025-11-13 17:46:47 [7b9fd68dd8e991ea9fd598ca015e10266498afc156969ccdfe67149124fd27cc]
2025-11-14T20:20:25-2965DCFB         Fri, 2025-11-14 20:20:25 [33539a1e5f2b83852cf5396ed442531d6b5d4cb2137522280285725c3ea5df48]
```

- If you're asked for a SSH password, set up access to your server via SSH key.
- If you're asked for a Borg repository password,
  [set up BORG_PASSCOMMAND](https://borgbackup.readthedocs.io/en/stable/usage/general.html#environment-variables).

> **NOTE** Any repository you want to use with Easyborg should be accessible on your terminal **without** password
> request.

### Configuration

Call _easyborg info_ to generate an empty config file and show its path:

```
$ easyborg info

Configuration:

  Config dir    /Users/user/Library/Application Support/easyborg/default
  Config file   /Users/user/Library/Application Support/easyborg/default/easyborg.toml
  Log dir       /Users/user/Library/Logs/easyborg/default
  Log file      /Users/user/Library/Logs/easyborg/default/easyborg.log
  Log level     INFO
  
...

```

If you're on a modern terminal, you may be able to click on a path to open it (Ctrl + click on iTerm2).
Open the config file, configure the folders you want to back up, and your backup and archive repositories.

## Usage

Easyborg currently supports five actions: _backup_, _archive_, _restore_, _extract_ and _delete_. Use

```
$ easyborg --help
```

for details.

## Concept

Easyborg makes a distinction between _backup_ and _archive_.

|             | Purpose                                    | Data Type         | Retention        |
|-------------|--------------------------------------------|-------------------|------------------|
| **Backup**  | Recovery in case of emergency (short-term) | Current, changing | Days to months   |
| **Archive** | Preservation for reference (long-term)     | Old, stable       | Years or forever |

### Backup

If you enable automatic backups, Easyborg will create a snapshot of all configured folders in each configured
**backup repository** every full hour. Meaning at 12:00, 13:00 and so on. Then, snapshots are pruned to save space.
So after the 13:00 snapshot is written, the 12:00 snapshot will be deleted. Here's how snapshots are retained:

- the last snapshot of the day for the past seven days
- one snapshot per week for the past three months

Any snapshot older than three months will be deleted.

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

### Relativization

If you _backup_ or _archive_ a folder, e.g.:

```
/Users/user/Documents
```

it will be stored in the snapshot as:

```
Users/user/Documents
```

When you _restore_ or _extract_ the folder, it will be written to the current working directory:

```
<CWD>/Users/user/Documents
```

This is a safety feature. If you _do_ want to overwrite the original folder, you can

- go to its parent folder (/ in the example) and run the restore action there, or
- remove the original folder and move the restored one (recommended)

### Glossary

| Easyborg           | Meaning                                                         | Borg             |
|--------------------|-----------------------------------------------------------------|------------------|
| Snapshot           | immutable point-in-time view of data                            | Archive          |
| Backup Repository  | storage of snapshots intended for recovery                      | Repository       |
| Archive Repository | storage of snapshots intended for preservation                  | Repository       |
| Backup (action)    | create snapshot in backup repository                            | `borg create`    |
| Archive (action)   | create snapshot in archive repository                           | `borg create`    |
| Extract (action)   | fetch selected items from snapshot                              | `borg extract`   | 
| Restore (action)   | fetch entire snapshot                                           | `borg extract`   |
| Repository URL     | Borg-style repository reference (local or remote)               | (same)           |
| Snapshot Location  | Borg-style snapshot reference (`repository_url::snapshot_name`) | Archive Location |

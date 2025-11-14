# Easyborg

Easyborg is a simple frontend for the awesome [BorgBackup](https://www.borgbackup.org/) (aka Borg) that uses
[fzf](https://github.com/junegunn/fzf) for user input.

This project is currently WIP and cannot be used yet.

## Screenshots

### Extract

<img src="https://haberey.com/easyborg/extract.gif" width="1024"  alt="Extract command in terminal"/>

### Backup

<img src="https://haberey.com/easyborg/backup.gif" width="1024"  alt="Backup command in terminal"/>

## Installation

TBD

## Usage

TBD

## Concept

Easyborg makes a distinction between _backup_ and _archive_.

|             | Purpose                                    | Data Type         | Retention        |
|-------------|--------------------------------------------|-------------------|------------------|
| **Backup**  | Recovery in case of emergency (short-term) | Current, changing | Days to months   |
| **Archive** | Preservation for reference (long-term)     | Old, stable       | Years or forever |

### Backup

If you enable automatic backups, Easyborg will create a snapshot of all configured folders in each configured
**backup repository** each full hour. Also, it will prune snapshots to save space. Here's how snapshots are
preserved:

- one per day for the past seven days
- one per week for the past three months

Any snapshot older than three months will be deleted.

> **NOTE** Pruning only occurs if _easyborg backup_ is called, manually or automatically.
> If you don't call it, your existing snapshots won't be touched.

### Archive

With Easyborg you can create a snapshot in each configured **archive repository** whenever you want. For example if
you decide to tidy up your documents folder, a good strategy would be:

1. Delete all files you want to get rid of forever (especially big files)
2. Archive the remaining files (that you want to keep) using _easyborg archive_
3. Delete all files you want to keep but don't need for your daily work

That way, you can start with a nice clean slate and still have all the documents you might need for later reference
stored safely in your archive repositories. Even if you accidentally deleted anything useful in step 1, you can still
restore it using your backup repositories.

Of course you can follow a different approach - it's up to you what you archive and when. Archive snapshots are never
pruned automatically. If you want to delete a snapshot, use _easyborg delete_.

### Relativization

If you _backup_ or _archive_ a folder like _/Users/user/Documents_, it will be stored in the snapshot as
_Users/user/Documents_. When you restore the folder, it will be written to
_CURRENT_WORKING_DIRECTORY/Users/user/Documents_ instead of overwriting the original folder.
This is a safety feature. If you _do_ want to overwrite the original folder, you can

- go to its parent folder (/ in the example) and run the restore action there, or
- remove the original folder and move the restored one (recommended)

### Glossary

| Easyborg term      | Meaning                                                         | Borg term        |
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

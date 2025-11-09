# easyborg

easyborg provides a simple workflow on top of [BorgBackup](https://www.borgbackup.org/) (aka Borg).

This project is currently WIP and cannot be used yet.

## Concept

easyborg distinguishes between _backup_ and _archive_ repositories:

|             | Purpose                                    | Data              | Retention        |
|-------------|--------------------------------------------|-------------------|------------------|
| **Backup**  | recovery in case of emergency (short-term) | current, changing | days to months   |
| **Archive** | preservation for reference (long-term)     | old, stable       | years or forever |

## Backup

easyborg creates snapshots of your configured backup folders regularly:

| Frequency | Availability |
|-----------|--------------|
| hourly    | 24 hours     |
| daily     | 7 days       |
| weekly    | 12 weeks     |
| monthly   | 12 months    |

## Archive

easyborg lets you create archive snapshots manually when needed.

Do this when you want to *keep a specific state*. Each folder is stored in its own snapshot to allow selective pruning
later.

## Glossary

| easyborg term      | Meaning                                                         | Borg term        |
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

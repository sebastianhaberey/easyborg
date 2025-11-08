# easyborg

easyborg - Borg for Dummies

easyborg provides a simple workflow on top of [BorgBackup](https://www.borgbackup.org/) aka Borg.

## Concept

easyborg distinguishes between _backup_ and _archive_ repositories:

| Aspect     | Backup (short-term)           | Archive (long-term)                  |
|------------|-------------------------------|--------------------------------------|
| Purpose    | recovery in case of emergency | preservation for long-term reference |
| Data State | current, changing             | old, stable                          |
| Retention  | days to months                | years or forever                     |

## Backup

easyborg creates snapshots of your configured backup folders regularly.

| Snapshot frequency | Availability |
|--------------------|--------------|
| hourly             | 24 hours     |
| daily              | 7 days       |
| weekly             | 12 weeks     |
| monthly            | 12 months    |

## Archive

Archiving is manual and intentional.

Do this when you want to *keep a specific state* for the long term.  
Each folder is stored in its own snapshot to allow selective pruning later.

## Glossary

| Term               | Meaning                                                         | Borg term        |
|--------------------|-----------------------------------------------------------------|------------------|
| Snapshot           | Immutable point-in-time view of data                            | Archive          |
| Backup Repository  | Storage of snapshots intended for recovery                      | Repository       |
| Archive Repository | Storage of snapshots intended for preservation                  | Repository       |
| Backup (action)    | Create snapshot in backup repository                            | `borg create`    |
| Archive (action)   | Create snapshot in archive repository                           | `borg create`    |
| Extract (action)   | Fetch selected items from snapshot                              | `borg extract`   | 
| Restore (action)   | Fetch entire snapshot                                           | `borg extract`   |
| Repository URL     | Borg-style repository reference (local or remote)               | (same)           |
| Snapshot Location  | Borg-style snapshot reference (`repository_url::snapshot_name`) | Archive Location |

# easyborg

Borg for Dummies

## Concept

easyborg distinguishes between _backup_ and _archive_:

| Aspect     | Backup                    | Archive            |
|------------|---------------------------|--------------------|
| Purpose    | Protect against emergency | Keep for reference |
| Data State | Current, changing         | Older, stable      |
| Retention  | Days to months            | Years or forever   |

## Backup

easyborg backs up your configured backup folders hourly and retains snapshots like this:

| Frequency     | Retainment        |
|---------------|-------------------|
| one per day   | past week         |
| one per week  | past three months |
| one per month | past year         |

## Archive

Archiving is triggered manually. Each folder will be saved in its own snapshot to facilitate later deletion.
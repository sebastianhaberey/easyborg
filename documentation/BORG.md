# BorgBackup Cheat Sheet

```bash
# create repository on external drive
borg init -e repokey /Volumes/BACKUP/repo

# create repository on server
borg init -e repokey user@backup.example.com:repo

# show repository key
borg key export /Volumes/BACKUP/repo

# list archives in remote repository
borg list ssh://user@backup.example.com/./repo

# list contents of remote archive
borg list ssh://user@backup.example.com/./repo::archive

# delete archive from local repository
borg delete /Volumes/BACKUP/repo::archive

# delete archive from remote repository
borg delete ssh://user@example.com/./repo::archive

# delete all archives from remote repository
borg delete ssh://user@example.com/./repo -a "*"

# break stale lock
borg break-lock ssh://user@example.com/./repo

# show repository key
borg key export /Volumes/BACKUP/repo
```
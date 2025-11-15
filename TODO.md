# TODO

## Release

- automatically create / copy config file if not found
- find out why easyborg info --profile production doesn't work (but easyborg --profile production info does)
- brew tap
- install on own system

## Later

- option for light mode (fzf)
- e2e test one repo fails -> next repo ok
- install command
- expert mode: prune options (--keep-xxx)
- expert mode: compact probability
- expert mode: cron options
- expert mode: output directory
- add status command (checks repository access and directory existence)
- implement long path strategy (1024 macOS / 4096 Linux ext4 )
- auto-completion (CLI)
- streamline logger vs console vs UI class

# DONE

- concept for configuration file location (dev vs prod)
- revisit Context class
- add expert mode
- add profiles option (changes log file / configuration file location)
- suppress stacktrace for user
- record screenshots
- clarify and document relativization
- delete command (select repo -> select snapshot -> delete)
- extract: remove contained paths (e.g. select "data", "data/firefox.dmg" -> only "data" needs to be extracted)
- show progress
- improve UI consistency (e.g. easyborg info vs help)
- add / remove crontab entry
- glossary
- dry run
- extract command
- prune and compact
- add comment to extract
- E2E tests
- logging (file)

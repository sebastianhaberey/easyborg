# TODO

## Soon

- move easyborg to src/easyborg
- install on own system and use
- automatic brew tap update via Github workflow
- add "secondary" text for all log outputs
- error on repository password request / ssh password request
- e2e test one repo fails -> next repo ok

## Later

- option for light mode (fzf)
- install command
- expert mode: prune options (--keep-xxx)
- expert mode: cron options
- expert mode: output directory
- add status command (checks repository access and directory existence)
- implement long path strategy (1024 macOS / 4096 Linux ext4 )
- auto-completion (CLI)
- streamline logger vs console vs UI class

# DONE

- add repository name to snapshot selection dialogs for safety
- brew tap
- update screenshots
- fixed bug where logging was not enabled properly
- remove quotes in output
- spinner instead of bar for indeterminate progress
- fix stacktrace behavior (see "easyborg dsable")
- find out where the extra console line comes from on "easyborg disable"
- "--debug" instead of "--log-level"
- test scheduled backups
- add log level option (expert)
- print stacktraces only if log level is DEBUG
- add environment variables (global and per repository) (e.g. BORG_PASSCOMMAND)
- automatically create / copy config file if not found
- find out why easyborg info --profile production doesn't work (but easyborg --profile production info does)
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

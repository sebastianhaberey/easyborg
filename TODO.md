# TODO

## Release

- error on repository password request / ssh password request
- remove quotes in output
- brew tap
- install on own system

## Later

- option for light mode (fzf)
- e2e test one repo fails -> next repo ok
- install command
- expert mode: prune options (--keep-xxx)
- expert mode: cron options
- expert mode: output directory
- add status command (checks repository access and directory existence)
- implement long path strategy (1024 macOS / 4096 Linux ext4 )
- auto-completion (CLI)
- streamline logger vs console vs UI class

# DONE

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

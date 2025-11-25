# Expert topics

## Shell completion

Generate completion file (zsh):

```
_EASYBORG_COMPLETE=zsh_source easyborg > ~/.easyborg-complete.zsh
```

Add to ~/.zshrc:

```
source ~/.easyborg-complete.zsh
```

See [Click documentation](click.palletsprojects.com/en/stable/shell-completion/) for bash, fish.

## Profiles

You can specify a profile under which Easyborg will run. If you don't specify a profile, the profile is "default".
As usual, running `easyborg info` with a profile will generate a configuration file:

```
easyborg --profile=production info
```


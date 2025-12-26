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
As usual, running `easyborg doctor` with a profile will show the path to the configuration file:

```
easyborg --profile=production doctor
```

## Themes

Set a theme via environment variable:

```
export EASYBORG_THEME=ice_dark
```

Available themes: melody_dark (default), melody_light, ice_dark, ice_light

## macOS Security

If you enable automatic backups on macOS, you may get this popup message:

> "python3.14" would like to access files in your Documents folder.

This happens if you want to back up protected folders like "Documents" or "Applications". If you need that, find out which
Python you run by running _easyborg doctor_. Open macOS -> System Settings -> Privacy and Security -> Full Disk Access
and drag one of the following onto it:

- The Python binary OR
- The directory that contains the Python binary

If it worked, macOS will create a new entry in the list. Set it to "enabled".

> **NOTE** Allowing Python full disk access is not without risk. If you install a malicious Homebrew package
> that uses Python, it will have full disk access.
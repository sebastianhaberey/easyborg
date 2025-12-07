# Screen recording

## asciinema

```
asciinema rec --title Easyborg --idle-time-limit 1 --window-size 120x20 --overwrite demo.cast
cd ..; source .venv/bin/activate; PROMPT='$ '; cd run; cls
asciinema play demo.cast
asciinema upload demo.cast
```
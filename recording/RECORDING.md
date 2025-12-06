# Screen recording

## asciinema

```
asciinema rec demo.cast --overwrite
cd ..; source .venv/bin/activate; PROMPT='$ '; cd run; cls
asciinema play demo.cast
asciinema upload demo.cast
```
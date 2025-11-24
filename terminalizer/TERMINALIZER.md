# Terminalizer screen recording

## Record and render

```
terminalizer record output -c config.yml
source .venv/bin/activate; PROMPT='$ '; cd run; cls
terminalizer render output.yml -q 1
```

Render again with -q 100 when satisfied (better colors).

## Pause at end

```
  - delay: 500
    content: "\0"
```

Repeat as needed.
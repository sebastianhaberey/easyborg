# Release Cheat Sheet

## Preparation

1. Update [CHANGELOG.md](../CHANGELOG.md)
2. Set version in [pyproject.toml](../pyproject.toml)

## Commands

```
# Create dedicated venv for release
python -m venv .venv-release

# Switch to new venv
source .venv-release/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install build and twine
pip install build twine

# Build
python -m build

# Install
pip install dist/easyborg-0.9.1rc2-py3-none-any.whl

# Run
easyborg info

# Upload to TestPyPi
twine upload --repository testpypi dist/*
```
# Release Cheat Sheet

## Preparation

1. Update [CHANGELOG.md](../CHANGELOG.md)
2. Set version in [pyproject.toml](../pyproject.toml)
3. Tag the version (e.g. v1.2.3) and push the tag

The PyPi release will be published automatically by a Github action.

## Build and test (manual)

```
# Remove old build artifacts
rm -rf dist/ .venv-release/

# Create dedicated venv for release
python -m venv .venv-release

# Switch to new venv
source .venv-release/bin/activate

# Upgrade pip, install build and twine
pip install --upgrade pip build twine

# Build
python -m build

# Install
pip install dist/easyborg-0.9.1rc2-py3-none-any.whl

# Run
easyborg info

# Uninstall 
pip uninstall -y easyborg
```

# Upload to TestPyPi

```
# Upload to TestPyPi (requires TestPyPi account, and API token in ~/.pypirc)
twine upload --repository testpypi dist/*

# Install from TestPyPi
pip install --index-url https://test.pypi.org/simple --extra-index-url https://pypi.org/simple easyborg==0.9.1rc2

# Run
easyborg info

# Uninstall
pip uninstall -y easyborg
```

## Deploy to PyPi

```
# Upload to PyPi
twine upload dist/*

# Install from PyPi
pipx install easyborg

# Uninstall
pipx uninstall easyborg
```

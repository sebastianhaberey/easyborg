# easyborg/__main__.py
from easyborg import ui
from easyborg.cli import cli

if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        ui.warn("Aborted by user.")
    except Exception as e:
        ui.error(f"Error: {e}")

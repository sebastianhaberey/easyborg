# easyborg/__main__.py
from easyborg import ui
from easyborg.cli import app

if __name__ == "__main__":
    try:
        app()
    except KeyboardInterrupt:
        ui.warn("Aborted by user.")
    except Exception as e:
        ui.error(f"Error: {e}")

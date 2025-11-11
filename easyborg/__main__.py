# easyborg/__main__.py
from easyborg import ui
from easyborg.cli import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        ui.warn("Aborted by user.")
    except Exception as e:
        ui.error(f"{e}")

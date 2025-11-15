from easyborg import ui
from easyborg.cli import cli


def main():
    try:
        ui.newline()
        cli()
    except Exception as e:
        ui.error(f"{e}")
        # ui.error(f"{e.__class__.__name__}: {e}")
        # raise e
    finally:
        ui.newline()


if __name__ == "__main__":
    main()

import typer

app = typer.Typer(help="easyborg - ")


@app.command()
def run(speed: int = typer.Argument(100, help="Motor speed (0-255).")):
    pass


@app.command()
def calibrate():
    pass


if __name__ == "__main__":
    app()

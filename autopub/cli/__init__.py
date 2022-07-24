import typer

app = typer.Typer()


@app.command()
def check():
    """This commands checks if the current PR has a valid release file."""

    print("preparing")


@app.command()
def build():
    print("building")


@app.command()
def publish():
    """
    1. commit
    2. release
    3. push on pypi or similar
    """
    print("publishing")

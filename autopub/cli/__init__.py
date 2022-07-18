import typer

app = typer.Typer()


@app.command()
def prepare():
    """This commands prepares the project for publishing.

    It gets information from the pull request like author, reviewers,
    contributors and release notes.
    """

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

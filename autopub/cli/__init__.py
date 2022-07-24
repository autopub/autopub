import typer

from autopub import Autopub
import rich

from autopub.exceptions import AutopubException
from rich.panel import Panel

app = typer.Typer()


@app.command()
def check():
    """This commands checks if the current PR has a valid release file."""

    autopub = Autopub()

    try:
        autopub.check()
    except AutopubException as e:
        rich.print(Panel.fit(f"[red]{e.message}"))

        raise typer.Exit(1)


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

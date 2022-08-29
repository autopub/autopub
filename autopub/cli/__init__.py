import typer

import rich
from rich.panel import Panel

from autopub import Autopub
from autopub.exceptions import AutopubException


app = typer.Typer()


@app.command()
def check():
    """This commands checks if the current PR has a valid release file."""

    autopub = Autopub()

    try:
        autopub.check()
    except AutopubException as e:
        rich.print(Panel.fit(f"[red]{e.message}"))

        raise typer.Exit(1) from e
    else:
        rich.print(Panel.fit("[green]Release file is valid"))


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

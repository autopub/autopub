from typing import TypedDict

import rich
import typer
from rich.panel import Panel

from autopub import Autopub
from autopub.cli.plugins import find_plugins
from autopub.exceptions import AutopubException

app = typer.Typer()


class State(TypedDict):
    plugins: list[str]


state: State = {"plugins": []}


@app.command()
def check():
    """This commands checks if the current PR has a valid release file."""

    autopub = Autopub(plugins=find_plugins(state["plugins"]))

    try:
        autopub.check()
    except AutopubException as e:
        rich.print(Panel.fit(f"[red]{e.message}"))

        raise typer.Exit(1) from e
    else:
        rich.print(Panel.fit("[green]Release file is valid"))


@app.command()
def build():
    autopub = Autopub(plugins=find_plugins(state["plugins"]))

    try:
        autopub.build()
    except AutopubException as e:
        rich.print(Panel.fit(f"[red]{e.message}"))

        raise typer.Exit(1) from e
    else:
        rich.print(Panel.fit("[green]Build succeeded"))


@app.command()
def publish():
    """
    1. commit
    2. release
    3. push on pypi or similar
    """
    print("publishing")


@app.callback()
def main(
    plugins: list[str] = typer.Option(
        [],
        "--plugin",
        "-p",
        help="List of plugins to use",
    )
):
    state["plugins"] = plugins

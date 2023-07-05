from typing import TypedDict

import rich
import typer
from rich.console import Group
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
        release_info = autopub.check()
    except AutopubException as e:
        rich.print(Panel.fit(f"[red]{e.message}"))

        raise typer.Exit(1) from e
    else:
        rich.print(
            Group(
                "[green]Release file is valid 🚀[/]\n\n"
                f"[bold]Release type:[/] {release_info.release_type}",
            )
        )


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
    autopub = Autopub(plugins=find_plugins(state["plugins"]))

    try:
        autopub.publish()
    except AutopubException as e:
        rich.print(Panel.fit(f"[red]{e.message}"))

        raise typer.Exit(1) from e
    else:
        rich.print(Panel.fit("[green]Publishing succeeded"))


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

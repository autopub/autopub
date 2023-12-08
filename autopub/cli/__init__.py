from typing import Optional, TypedDict

import rich
import typer
from rich.console import Group
from rich.markdown import Markdown
from rich.padding import Padding
from rich.panel import Panel
from typing_extensions import Annotated

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
            Padding(
                Group(
                    (
                        "[bold on bright_magenta] Release type: [/] "
                        f"[yellow italic underline]{release_info.release_type}[/]\n"
                    ),
                    "[bold on bright_magenta] Release notes: [/]\n",
                    Markdown(release_info.release_notes),
                    "\n---\n\n[green bold]Release file is valid![/] 🚀",
                ),
                (1, 1),
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
def prepare():
    autopub = Autopub(plugins=find_plugins(state["plugins"]))

    try:
        autopub.prepare()
    except AutopubException as e:
        rich.print(Panel.fit(f"[red]{e.message}"))

        raise typer.Exit(1) from e
    else:
        rich.print(Panel.fit("[green]Preparation succeeded"))


@app.command()
def publish(
    repository: Annotated[
        Optional[str],
        typer.Option("--repository", "-r", help="Repository to publish to"),
    ] = None,
):
    autopub = Autopub(plugins=find_plugins(state["plugins"]))

    try:
        autopub.publish(repository=repository)
    except AutopubException as e:
        rich.print(Panel.fit(f"[red]{e.message}"))

        raise typer.Exit(1) from e
    else:
        rich.print(Panel.fit("[green]Publishing succeeded"))


@app.callback(invoke_without_command=True)
def main(
    plugins: list[str] = typer.Option(
        [],
        "--plugin",
        "-p",
        help="List of plugins to use",
    ),
    should_show_version: Annotated[
        Optional[bool], typer.Option("--version", is_eager=True)
    ] = None,
):
    state["plugins"] = plugins
    state["plugins"].extend(["update_changelog", "bump_version"])

    if should_show_version:
        from importlib.metadata import version

        print(version("autopub"))

        raise typer.Exit()

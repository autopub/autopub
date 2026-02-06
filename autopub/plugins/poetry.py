from __future__ import annotations

from autopub.plugins import AutopubPackageManagerPlugin
from autopub.plugins.bump_version import BumpVersionPlugin

__all__ = ["PoetryPlugin"]


class PoetryPlugin(BumpVersionPlugin, AutopubPackageManagerPlugin):
    def build(self) -> None:
        self.run_command(["poetry", "build"])

    def publish(self, repository: str | None = None, **kwargs: str) -> None:
        additional_args: list[str] = []

        if repository:
            additional_args += ["--repository", repository]

        self.run_command(["poetry", "publish", *additional_args])

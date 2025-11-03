from __future__ import annotations

from typing import Any

from autopub.plugins import AutopubPackageManagerPlugin
from autopub.plugins.bump_version import BumpVersionPlugin

__all__ = ["PDMPlugin"]


class PDMPlugin(BumpVersionPlugin, AutopubPackageManagerPlugin):
    def build(self) -> None:
        self.run_command(["pdm", "build"])

    def publish(self, repository: str | None = None, **kwargs: Any) -> None:
        additional_args: list[str] = []

        if repository:
            additional_args += ["--repository", repository]

        self.run_command(["pdm", "publish", *additional_args])

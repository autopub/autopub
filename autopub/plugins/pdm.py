from __future__ import annotations

from typing import Any

from autopub.plugins import AutopubPackageManagerPlugin, AutopubPlugin


class PDMPlugin(AutopubPlugin, AutopubPackageManagerPlugin):
    def build(self) -> None:
        self.run_command(["pdm", "build"])

    def publish(self, repository: str | None = None, **kwargs: Any) -> None:
        additional_args: list[str] = []

        if repository:
            additional_args += ["--repository", repository]

        self.run_command(["pdm", "publish", *additional_args])

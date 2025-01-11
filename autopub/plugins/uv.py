from __future__ import annotations

from typing import Any

from autopub.plugins import AutopubPackageManagerPlugin, AutopubPlugin


class UvPlugin(AutopubPlugin, AutopubPackageManagerPlugin):
    def build(self) -> None:
        self.run_command(["uv", "build"])

    def publish(self, repository: str | None = None, **kwargs: Any) -> None:
        additional_args: list[str] = []

        if repository:
            raise ValueError("Not yet implemented")

        if publish_url := kwargs.get("publish_url"):
            additional_args.append("--publish-url")
            additional_args.append(publish_url)

        if username := kwargs.get("username"):
            additional_args.append("--username")
            additional_args.append(username)

        if password := kwargs.get("password"):
            additional_args.append("--password")
            additional_args.append(password)

        if token := kwargs.get("token"):
            additional_args.append("--token")
            additional_args.append(token)

        self.run_command(["uv", "publish", *additional_args])

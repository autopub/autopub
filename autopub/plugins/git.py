from __future__ import annotations

from typing import Any

from autopub.plugins import AutopubPlugin


class GitPlugin(AutopubPlugin):
    def post_publish(self, repository: str | None = None, **kwargs: Any) -> None:
        self.run_command(["git", "add", "."])

        self.run_command(["git", "commit", "-m", "🤖 autopub publish"])

        self.run_command(["git", "push"])

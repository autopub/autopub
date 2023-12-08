from __future__ import annotations

from autopub.plugins import AutopubPlugin
from autopub.types import ReleaseInfoWithVersion


class GitPlugin(AutopubPlugin):
    def post_publish(self, release_info: ReleaseInfoWithVersion) -> None:
        tag_name = release_info.version

        self.run_command(["git", "config", "--global", "user.email", "autopub@autopub"])
        self.run_command(["git", "config", "--global", "user.name", "autopub"])

        self.run_command(["git", "tag", tag_name])

        # TODO: config?
        self.run_command(["git", "rm", "RELEASE.md"])
        self.run_command(["git", "add", "--all", "--", ":!main/.autopub"])
        self.run_command(["git", "commit", "-m", "🤖 autopub publish"])
        self.run_command(["git", "push"])
        self.run_command(["git", "push", "origin", tag_name])

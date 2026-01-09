from __future__ import annotations

from autopub.plugins import AutopubPlugin
from autopub.types import ReleaseInfo

COMMIT_TEMPLATE = """\
🤖 Release {release_info.version}

{release_info.release_notes}

[skip ci]
"""


class GitPlugin(AutopubPlugin):
    def post_publish(self, release_info: ReleaseInfo) -> None:
        assert release_info.version is not None

        tag_name = release_info.version

        self.run_command(["git", "config", "--global", "user.email", "autopub@autopub"])
        self.run_command(["git", "config", "--global", "user.name", "autopub"])

        self.run_command(["git", "tag", tag_name])

        commit_message = COMMIT_TEMPLATE.format(release_info=release_info)

        # TODO: config?
        self.run_command(["git", "rm", "RELEASE.md"])
        self.run_command(["git", "add", "--all", "--", ":!.autopub"])
        self.run_command(["git", "commit", "-m", commit_message])
        self.run_command(["git", "push"])
        self.run_command(["git", "push", "origin", tag_name])

from __future__ import annotations

import os
import subprocess

from pydantic import BaseModel, Field

from autopub.exceptions import CommandFailed
from autopub.plugins import AutopubPlugin
from autopub.types import ReleaseInfo

COMMIT_TEMPLATE = """\
🤖 Release {release_info.version}

{release_info.release_notes}

[skip ci]
"""


class GitConfig(BaseModel):
    """Git configuration for autopub."""

    git_username: str = Field(
        default="autopub",
        description="Git username for commits",
        validation_alias="git-username",
    )
    git_email: str = Field(
        default="autopub@autopub",
        description="Git email for commits",
        validation_alias="git-email",
    )


class GitPlugin(AutopubPlugin):
    id = "git"
    Config = GitConfig

    def _is_autopub_ignored(self) -> bool:
        command = ["git", "check-ignore", "-q", ".autopub"]
        result = subprocess.run(command, env=os.environ.copy())

        if result.returncode in (0, 1):
            return result.returncode == 0

        raise CommandFailed(command=command, returncode=result.returncode)

    def _get_git_username(self) -> str:
        """Get git username from environment variable or config."""
        env_value = os.environ.get("GIT_USERNAME")
        if env_value:
            return env_value

        if self._config:
            return self.config.git_username  # type: ignore

        return "autopub"

    def _get_git_email(self) -> str:
        """Get git email from environment variable or config."""
        env_value = os.environ.get("GIT_EMAIL")
        if env_value:
            return env_value

        if self._config:
            return self.config.git_email  # type: ignore

        return "autopub@autopub"

    def post_publish(self, release_info: ReleaseInfo) -> None:
        assert release_info.version is not None

        tag_name = release_info.version

        git_email = self._get_git_email()
        git_username = self._get_git_username()

        self.run_command(["git", "config", "--global", "user.email", git_email])
        self.run_command(["git", "config", "--global", "user.name", git_username])

        self.run_command(["git", "tag", tag_name])

        commit_message = COMMIT_TEMPLATE.format(release_info=release_info)

        # TODO: config?
        self.run_command(["git", "rm", "RELEASE.md"])
        if self._is_autopub_ignored():
            self.run_command(["git", "add", "--all"])
        else:
            self.run_command(["git", "add", "--all", "--", ":!.autopub"])
        self.run_command(["git", "commit", "-m", commit_message])
        self.run_command(["git", "push"])
        self.run_command(["git", "push", "origin", tag_name])

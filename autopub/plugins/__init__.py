from __future__ import annotations

import subprocess
from typing import Any, Protocol, runtime_checkable

from autopub.exceptions import AutopubException, CommandFailed
from autopub.types import ReleaseInfo


class AutopubPlugin:
    data: dict[str, object] = {}

    def run_command(self, command: list[str]) -> None:
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            raise CommandFailed(command=command, returncode=e.returncode) from e

    def prepare(self, release_info: ReleaseInfo) -> None:
        ...

    def validate_release_notes(self, release_info: ReleaseInfo):
        ...

    def on_release_notes_valid(self, release_info: ReleaseInfo):
        ...

    def on_release_notes_invalid(self, exception: AutopubException):
        ...


@runtime_checkable
class AutopubPackageManagerPlugin(Protocol):
    def build(self) -> None:
        ...

    def publish(self, repository: str | None = None, **kwargs: Any) -> None:
        ...

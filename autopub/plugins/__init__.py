from __future__ import annotations

import os
import subprocess
from typing import Any, Protocol, runtime_checkable

from autopub.exceptions import AutopubException, CommandFailed
from autopub.types import ReleaseInfo


class AutopubPlugin:
    data: dict[str, object] = {}

    def run_command(self, command: list[str]) -> None:
        try:
            subprocess.run(command, check=True, env=os.environ.copy())
        except subprocess.CalledProcessError as e:
            raise CommandFailed(command=command, returncode=e.returncode) from e

    def post_check(self, release_info: ReleaseInfo) -> None:  # pragma: no cover
        ...

    def prepare(self, release_info: ReleaseInfo) -> None:  # pragma: no cover
        ...

    def post_prepare(self, release_info: ReleaseInfo) -> None:  # pragma: no cover
        ...

    def validate_release_notes(
        self, release_info: ReleaseInfo
    ) -> None:  # pragma: no cover
        ...

    def on_release_notes_valid(
        self, release_info: ReleaseInfo
    ) -> None:  # pragma: no cover
        ...

    def on_release_notes_invalid(
        self, exception: AutopubException
    ) -> None:  # pragma: no cover
        ...

    def post_publish(self, release_info: ReleaseInfo) -> None:  # pragma: no cover
        ...


@runtime_checkable
class AutopubPackageManagerPlugin(Protocol):
    def build(self) -> None:  # pragma: no cover
        ...

    def publish(
        self, repository: str | None = None, **kwargs: Any
    ) -> None:  # pragma: no cover
        ...

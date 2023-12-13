from __future__ import annotations

import os
import subprocess
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel

from autopub.exceptions import AutopubException, CommandFailed
from autopub.types import ReleaseInfo

if TYPE_CHECKING:
    from autopub import ConfigType

Config = TypeVar("Config", bound=BaseModel)


class AutopubPlugin:
    id: str
    data: dict[str, object] = {}

    def validate_config(self, config: ConfigType):
        configuration_class: type[BaseModel] | None = getattr(self, "Config", None)

        if configuration_class is None:
            return

        plugin_config = config.get(self.id, {})

        self.configuration = configuration_class.model_validate(plugin_config)

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

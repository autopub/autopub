from __future__ import annotations

import os
import subprocess
from collections.abc import Mapping
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

    _config: ConfigType | None = None

    def validate_config(self, config: ConfigType):
        configuration_class: type[BaseModel] | None = getattr(self, "Config", None)

        if configuration_class is None:
            return

        # Support both tool.autopub.plugins.<id> and tool.autopub.plugin_config.<id>
        plugins_value = config.get("plugins", {})

        # plugins can be a list of plugin module paths (e.g. ["autopub.plugins.github"])
        # or a dict of plugin configs (e.g. {"git": {...}}). Only use .get() if it's a dict.
        if isinstance(plugins_value, Mapping):
            plugin_config = plugins_value.get(self.id, {})
        else:
            plugin_config = {}

        if not plugin_config:
            # Fallback to legacy plugin_config location
            plugin_config = config.get("plugin_config", {}).get(self.id, {})

        self._config = configuration_class.model_validate(plugin_config)

    @property
    def config(self) -> ConfigType:
        assert self._config is not None
        return self._config

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

    def on_release_file_not_found(self) -> None:  # pragma: no cover
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

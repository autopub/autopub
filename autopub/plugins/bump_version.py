from __future__ import annotations

import pathlib

import tomlkit
from dunamai import Version

from autopub.plugins import AutopubPlugin
from autopub.types import ReleaseInfo


class BumpVersionPlugin(AutopubPlugin):
    @property
    def pyproject_config(self) -> tomlkit.TOMLDocument:
        content = pathlib.Path("pyproject.toml").read_text()

        return tomlkit.parse(content)

    def _get_version(self, config: tomlkit.TOMLDocument) -> str:
        try:
            return config["tool"]["poetry"]["version"]  # type: ignore
        except KeyError:
            return config["project"]["version"]  # type: ignore

    def _update_version(self, config: tomlkit.TOMLDocument, new_version: str) -> None:
        try:
            config["tool"]["poetry"]["version"] = new_version  # type: ignore
        except KeyError:
            config["project"]["version"] = new_version  # type: ignore

    def prepare(self, release_info: ReleaseInfo) -> None:
        config = self.pyproject_config

        version = Version(self._get_version(config))

        bump_type = {"major": 0, "minor": 1, "patch": 2}[release_info.release_type]
        new_version = version.bump(bump_type).serialize()

        self.data["old_version"] = version.serialize()
        self.data["new_version"] = new_version

        self._update_version(config, new_version)

        pathlib.Path("pyproject.toml").write_text(tomlkit.dumps(config))  # type: ignore

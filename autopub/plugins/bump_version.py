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

    def post_check(self, release_info: ReleaseInfo) -> None:
        config = self.pyproject_config

        bump_type = {"major": 0, "minor": 1, "patch": 2}[release_info.release_type]

        version = Version(self._get_version(config))

        release_info.previous_version = str(version)
        release_info.version = version.bump(bump_type).serialize()

        self._update_version(config, release_info.version)

        pathlib.Path("pyproject.toml").write_text(tomlkit.dumps(config))  # type: ignore

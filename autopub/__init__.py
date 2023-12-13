from __future__ import annotations

import hashlib
import json
from functools import cached_property
from pathlib import Path
from typing import Iterable, Mapping, TypeAlias

import frontmatter
import tomlkit
from pydantic import ValidationError

from autopub.exceptions import (
    ArtifactHashMismatch,
    ArtifactNotFound,
    AutopubException,
    InvalidConfiguration,
    NoPackageManagerPluginFound,
    ReleaseFileEmpty,
    ReleaseFileNotFound,
    ReleaseNotesEmpty,
    ReleaseTypeInvalid,
    ReleaseTypeMissing,
)
from autopub.plugin_loader import load_plugins
from autopub.plugins import (
    AutopubPackageManagerPlugin,
    AutopubPlugin,
)
from autopub.types import ReleaseInfo

ConfigValue: TypeAlias = (
    None | bool | str | float | int | list["ConfigValue"] | Mapping[str, "ConfigValue"]
)

ConfigType = Mapping[str, ConfigValue]


class Autopub:
    RELEASE_FILE_PATH = "RELEASE.md"
    plugins: list[AutopubPlugin]

    def __init__(self, plugins: Iterable[type[AutopubPlugin]] = ()) -> None:
        self.plugins = [plugin_class() for plugin_class in plugins]

        self.load_plugins()

    @cached_property
    def config(self) -> ConfigType:
        pyproject_path = Path.cwd() / "pyproject.toml"

        if not Path("pyproject.toml").exists():
            return {}

        content = pyproject_path.read_text()

        data = tomlkit.parse(content)

        return data.get("tool", {}).get("autopub", {})  # type: ignore

    @property
    def release_file(self) -> Path:
        return Path.cwd() / self.RELEASE_FILE_PATH

    @property
    def release_notes(self) -> str:
        return self.release_file.read_text()

    @property
    def release_file_hash(self) -> str:
        return hashlib.sha256(self.release_notes.encode("utf-8")).hexdigest()

    @property
    def release_info_file(self) -> Path:
        return Path(".autopub") / "release_info.json"

    @property
    def release_info(self) -> ReleaseInfo:
        if not self.release_info_file.exists():
            raise ArtifactNotFound()

        release_info = json.loads(self.release_info_file.read_text())

        if release_info["hash"] != self.release_file_hash:
            raise ArtifactHashMismatch()

        return ReleaseInfo.from_dict(release_info)

    def load_plugins(self, default_plugins: list[str] | None = None) -> None:
        default_plugins = default_plugins or []

        additional_plugins: list[str] = self.config.get("plugins", [])  # type: ignore

        all_plugins = default_plugins + additional_plugins

        plugins = load_plugins(all_plugins)

        self.plugins += [plugin_class() for plugin_class in plugins]

    def check(self) -> None:
        release_file = Path(self.RELEASE_FILE_PATH)

        if not release_file.exists():
            raise ReleaseFileNotFound()

        try:
            release_info = self._validate_release_notes(self.release_notes)
        except AutopubException as e:
            for plugin in self.plugins:
                plugin.on_release_notes_invalid(e)
            raise

        for plugin in self.plugins:
            plugin.on_release_notes_valid(release_info)

        for plugin in self.plugins:
            plugin.post_check(release_info)

        self._write_artifact(release_info)

    def build(self) -> None:
        if not any(
            isinstance(plugin, AutopubPackageManagerPlugin) for plugin in self.plugins
        ):
            raise NoPackageManagerPluginFound()

        for plugin in self.plugins:
            if isinstance(plugin, AutopubPackageManagerPlugin):
                plugin.build()

    def prepare(self) -> None:
        release_info = self.release_info

        for plugin in self.plugins:
            plugin.prepare(release_info)

        for plugin in self.plugins:
            plugin.post_prepare(release_info)

        self._write_artifact(release_info)

    def publish(self, repository: str | None = None) -> None:
        release_info = self.release_info

        for plugin in self.plugins:
            # TODO: maybe pass release info to publish method?
            if isinstance(plugin, AutopubPackageManagerPlugin):
                plugin.publish(repository=repository)

        for plugin in self.plugins:
            plugin.post_publish(release_info)

        self._delete_release_file()

    def validate_config(self) -> None:
        errors: dict[str, ValidationError] = {}

        for plugin in self.plugins:
            try:
                plugin.validate_config(self.config)
            except ValidationError as e:
                errors[plugin.id] = e

        if errors:
            raise InvalidConfiguration(errors)

    def _delete_release_file(self) -> None:
        self.release_file.unlink(missing_ok=True)

    def _write_artifact(self, release_info: ReleaseInfo) -> None:
        data = {
            **release_info.dict(),
            "hash": self.release_file_hash,
        }

        self.release_info_file.parent.mkdir(exist_ok=True)
        self.release_info_file.write_text(json.dumps(data))

    def _deprecated_load(self, release_notes: str) -> ReleaseInfo:
        # supports loading of old release notes format, which is
        # deprecated and will be removed in a future release
        # and looks like this:
        # Release type: patch
        # release notes here.

        try:
            release_info, release_notes = release_notes.split("\n", 1)
        except ValueError as e:
            raise ReleaseTypeMissing() from e

        release_info = release_info.lower()

        if not release_info.startswith("release type:"):
            raise ReleaseTypeMissing()

        release_type = release_info.split(":", 1)[1].strip().lower()

        return ReleaseInfo(
            release_type=release_type, release_notes=release_notes.strip()
        )

    def _load_from_frontmatter(self, release_notes: str) -> ReleaseInfo:
        # supports loading of new release notes format, which looks like this:
        # ---
        # release type: patch
        # ---
        # release notes here.

        post = frontmatter.loads(release_notes)

        data: dict[str, str] = post.to_dict()

        release_type = data.pop("release type").lower()

        if release_type not in ("major", "minor", "patch"):
            raise ReleaseTypeInvalid(release_type)

        if post.content.strip() == "":
            raise ReleaseNotesEmpty()

        return ReleaseInfo(
            release_type=release_type,
            release_notes=post.content,
            additional_info=data,
            version=None,
            previous_version=None,
        )

    def _validate_release_notes(self, release_notes: str) -> ReleaseInfo:
        if not release_notes:
            raise ReleaseFileEmpty()

        try:
            release_info = self._load_from_frontmatter(release_notes)
        except KeyError:
            release_info = self._deprecated_load(release_notes)

        for plugin in self.plugins:
            plugin.validate_release_notes(release_info)

        return release_info

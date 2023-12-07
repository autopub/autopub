from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from pathlib import Path

import frontmatter

from autopub.exceptions import (
    ArtifactHashMismatch,
    ArtifactNotFound,
    AutopubException,
    NoPackageManagerPluginFound,
    ReleaseFileEmpty,
    ReleaseFileNotFound,
    ReleaseNotesEmpty,
    ReleaseTypeInvalid,
    ReleaseTypeMissing,
)
from autopub.plugins import AutopubPackageManagerPlugin, AutopubPlugin
from autopub.types import ReleaseInfo


class Autopub:
    RELEASE_FILE_PATH = "RELEASE.md"

    def __init__(self, plugins: Iterable[type[AutopubPlugin]] = ()) -> None:
        self.plugins = [plugin_class() for plugin_class in plugins]

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
    def release_data_file(self) -> Path:
        return Path(".autopub") / "release_data.json"

    # TODO: typed dict
    @property
    def release_data(self) -> ReleaseInfo:
        if not self.release_data_file.exists():
            raise ArtifactNotFound()

        release_data = json.loads(self.release_data_file.read_text())

        if release_data["hash"] != self.release_file_hash:
            raise ArtifactHashMismatch()

        return ReleaseInfo(
            release_type=release_data["release_type"],
            release_notes=release_data["release_notes"],
            additional_info=release_data["plugin_data"],
        )

    def check(self) -> ReleaseInfo:
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

        self._write_artifact(release_info)

        return release_info

    def build(self) -> None:
        if not any(
            isinstance(plugin, AutopubPackageManagerPlugin) for plugin in self.plugins
        ):
            raise NoPackageManagerPluginFound()

        for plugin in self.plugins:
            if isinstance(plugin, AutopubPackageManagerPlugin):
                plugin.build()

    def prepare(self) -> None:
        for plugin in self.plugins:
            plugin.prepare(self.release_data)

    def publish(self, repository: str | None) -> None:
        # TODO: shall we put this in a function, to make it
        # clear that we are triggering the logic to check the release file?
        self.release_data

        for plugin in self.plugins:
            if isinstance(plugin, AutopubPackageManagerPlugin):
                plugin.publish(repository=repository)

    def _write_artifact(self, release_info: ReleaseInfo) -> None:
        data = {
            "hash": self.release_file_hash,
            "release_type": release_info.release_type,
            "release_notes": release_info.release_notes,
            "plugin_data": {
                key: value
                for plugin in self.plugins
                for key, value in plugin.data.items()
            },
        }

        self.release_data_file.parent.mkdir(exist_ok=True)
        self.release_data_file.write_text(json.dumps(data))

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

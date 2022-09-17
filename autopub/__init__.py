from pathlib import Path
from typing import Iterable, Type

# TODO: add stubs
import frontmatter  # type: ignore

from .exceptions import (
    AutopubException,
    InvalidReleaseType,
    MissingReleaseType,
    NoPackageManagerPluginFound,
    ReleaseFileEmpty,
    ReleaseFileNotFound,
    ReleaseNoteInvalid,
)
from .plugins import AutopubPackageManagerPlugin, AutopubPlugin
from .types import ReleaseInfo


class Autopub:
    RELEASE_FILE_PATH = "RELEASE.md"

    def __init__(self, plugins: Iterable[Type[AutopubPlugin]] = ()) -> None:
        self.plugins = [plugin_class() for plugin_class in plugins]

    def check(self) -> ReleaseInfo:
        release_file = Path(self.RELEASE_FILE_PATH)

        if not release_file.exists():
            raise ReleaseFileNotFound()

        content = release_file.read_text()

        try:
            release_info  = self._validate_release_notes(content)
        except AutopubException as e:
            for plugin in self.plugins:
                plugin.on_release_notes_invalid(e)
            raise

        for plugin in self.plugins:
            plugin.on_release_notes_valid(release_info)

        return release_info

    def build(self) -> None:
        if not any(
            isinstance(plugin, AutopubPackageManagerPlugin) for plugin in self.plugins
        ):
            raise NoPackageManagerPluginFound()

        for plugin in self.plugins:
            if isinstance(plugin, AutopubPackageManagerPlugin):
                plugin.build()

    def _deprecated_load(self, release_notes: str) -> ReleaseInfo:
        # supports loading of old release notes format, which is
        # deprecated and will be removed in a future release
        # and looks like this:
        # Release type: patch
        # release notes here.

        try:
            release_info, release_notes = release_notes.split("\n", 1)
        except ValueError as e:
            raise MissingReleaseType() from e

        release_info = release_info.lower()

        if not release_info.startswith("release type:"):
            raise MissingReleaseType()

        release_type = release_info.split(":", 1)[1].strip().lower()

        return ReleaseInfo(release_type=release_type, release_notes=release_notes.strip())

    def _load_from_frontmatter(self, release_notes: str) -> ReleaseInfo:
        # supports loading of new release notes format, which looks like this:
        # ---
        # release type: patch
        # ---
        # release notes here.

        # TODO: check for invalid frontmatter
        post = frontmatter.loads(release_notes)

        data: dict[str, str] = post.to_dict()

        release_type = data.pop("release type").lower()

        if release_type not in ("major", "minor", "patch"):
            raise InvalidReleaseType(release_type)

        return ReleaseInfo(
            release_type=release_type,
            release_notes=post.content,
            additional_info=data,
        )

    def _validate_release_notes(self, release_notes: str) -> ReleaseInfo:
        if not release_notes:
            raise ReleaseFileEmpty()

        additional_info = frontmatter.loads(release_notes)

        try:
            release_info =  self._load_from_frontmatter(release_notes)
        except KeyError:
            release_info = self._deprecated_load(release_notes)

        for plugin in self.plugins:
            plugin.validate_release_notes(release_info)

        return release_info

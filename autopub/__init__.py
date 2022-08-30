from pathlib import Path
from typing import Iterable, Tuple, Type

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


class Autopub:
    RELEASE_FILE_PATH = "RELEASE.md"

    def __init__(self, plugins: Iterable[Type[AutopubPlugin]] = ()) -> None:
        self.plugins = [plugin_class() for plugin_class in plugins]

    def check(self) -> None:
        release_file = Path(self.RELEASE_FILE_PATH)

        if not release_file.exists():
            raise ReleaseFileNotFound()

        content = release_file.read_text()

        try:
            release_type, release_notes = self._validate_release_notes(content)
        except AutopubException as e:
            for plugin in self.plugins:
                plugin.on_release_notes_invalid(e)
            raise

        for plugin in self.plugins:
            plugin.on_release_notes_valid(release_notes)

    def build(self) -> None:
        if not any(
            isinstance(plugin, AutopubPackageManagerPlugin) for plugin in self.plugins
        ):
            raise NoPackageManagerPluginFound()

        for plugin in self.plugins:
            if isinstance(plugin, AutopubPackageManagerPlugin):
                plugin.build()

    def _validate_release_notes(self, release_notes: str) -> Tuple[str, str]:
        if not release_notes:
            raise ReleaseFileEmpty()

        try:
            release_info, release_notes = release_notes.split("\n", 1)
        except ValueError as e:
            raise ReleaseNoteInvalid() from e

        release_info = release_info.lower()

        if not release_info.startswith("release type:"):
            raise MissingReleaseType()

        release_type = release_info.split(":", 1)[1].strip().lower()

        if release_type not in ("major", "minor", "patch"):
            raise InvalidReleaseType(release_type)

        for plugin in self.plugins:
            plugin.validate_release_notes(release_notes)

        return release_type, release_notes.strip()

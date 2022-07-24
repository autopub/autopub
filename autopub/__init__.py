from pathlib import Path
from typing import Iterable, Type

from .exceptions import (ReleaseFileEmpty, ReleaseFileNotFound,
                         ReleaseNoteInvalid, MissingReleaseType, InvalidReleaseType)


class Autopub:
    RELEASE_FILE_PATH = "RELEASE.md"

    def __init__(self, plugins: Iterable[Type] = ()) -> None:
        self.plugins = [plugin_class() for plugin_class in plugins]

    def check(self) -> None:
        release_file = Path(self.RELEASE_FILE_PATH)

        if not release_file.exists():
            raise ReleaseFileNotFound()

        content = release_file.read_text()

        self._validate_release_notes(content)

    def _validate_release_notes(self, release_notes: str):
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

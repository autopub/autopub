from pathlib import Path

from .exceptions import (ReleaseFileEmpty, ReleaseFileNotFound,
                         ReleaseNoteInvalid, MissingReleaseType, InvalidReleaseType)


class Autopub:
    RELEASE_FILE_PATH = "RELEASE.md"

    def check(self) -> None:
        release_file = Path(self.RELEASE_FILE_PATH)

        if not release_file.exists():
            raise ReleaseFileNotFound()

        content = release_file.read_text()

        self._validate_release_note(content)

    def _validate_release_note(self, release_note: str):
        if not release_note:
            raise ReleaseFileEmpty()

        try:
            release_info, release_note = release_note.split("\n", 1)
        except ValueError as e:
            raise ReleaseNoteInvalid() from e

        release_info = release_info.lower()

        if not release_info.startswith("release type:"):
            raise MissingReleaseType()

        release_type = release_info.split(":", 1)[1].strip().lower()

        if release_type not in ("major", "minor", "patch"):
            raise InvalidReleaseType(release_type)

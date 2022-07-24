from pathlib import Path

import pytest
from autopub import Autopub
from autopub.exceptions import ReleaseFileEmpty, ReleaseFileNotFound, ReleaseNoteInvalid, MissingReleaseType, InvalidReleaseType


def test_check_fails_if_no_release_file_is_present(tmpdir):
    with tmpdir.as_cwd():
        autopub = Autopub()

        with pytest.raises(ReleaseFileNotFound):
            autopub.check()


def test_works(tmpdir, valid_release_text: str):
    release_file = Path(tmpdir) / "RELEASE.md"
    release_file.write_text(valid_release_text)

    with tmpdir.as_cwd():
        autopub = Autopub()

        autopub.check()


def test_fails_if_release_note_is_empty(tmpdir):
    release_file = Path(tmpdir) / "RELEASE.md"
    release_file.write_text("")

    with tmpdir.as_cwd():
        autopub = Autopub()

        with pytest.raises(ReleaseFileEmpty):
            autopub.check()


def test_fails_if_release_is_bad(tmpdir):
    release_file = Path(tmpdir) / "RELEASE.md"
    release_file.write_text("This is not a valid release note")

    with tmpdir.as_cwd():
        autopub = Autopub()

        with pytest.raises(ReleaseNoteInvalid):
            autopub.check()


def test_fails_if_release_file_is_missing_release_type(tmpdir):
    release_file = Path(tmpdir) / "RELEASE.md"
    release_file.write_text("Example \nThis is not a valid release note")

    with tmpdir.as_cwd():
        autopub = Autopub()

        with pytest.raises(MissingReleaseType):
            autopub.check()


def test_fails_if_release_type_is_not_valid(tmpdir):
    release_file = Path(tmpdir) / "RELEASE.md"
    release_file.write_text("Release type: butter\nThis is not a valid release note")

    with tmpdir.as_cwd():
        autopub = Autopub()

        with pytest.raises(InvalidReleaseType):
            autopub.check()

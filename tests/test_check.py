from pathlib import Path

import pytest
from autopub import Autopub
from autopub.exceptions import ReleaseFileEmpty, ReleaseFileNotFound, ReleaseNoteInvalid, MissingReleaseType, InvalidReleaseType


@pytest.fixture
def temporary_working_directory(tmpdir):
    with tmpdir.as_cwd():
        yield tmpdir


def test_check_fails_if_no_release_file_is_present(temporary_working_directory):
    autopub = Autopub()

    with pytest.raises(ReleaseFileNotFound):
        autopub.check()


def test_works(temporary_working_directory, valid_release_text: str):
    release_file = Path(temporary_working_directory) / "RELEASE.md"
    release_file.write_text(valid_release_text)

    autopub = Autopub()
    autopub.check()


def test_fails_if_release_note_is_empty(temporary_working_directory):
    release_file = Path(temporary_working_directory) / "RELEASE.md"
    release_file.write_text("")

    autopub = Autopub()

    with pytest.raises(ReleaseFileEmpty):
        autopub.check()


def test_fails_if_release_is_bad(temporary_working_directory):
    release_file = Path(temporary_working_directory) / "RELEASE.md"
    release_file.write_text("This is not a valid release note")

    autopub = Autopub()

    with pytest.raises(ReleaseNoteInvalid):
        autopub.check()


def test_fails_if_release_file_is_missing_release_type(temporary_working_directory):
    release_file = Path(temporary_working_directory) / "RELEASE.md"
    release_file.write_text("Example \nThis is not a valid release note")

    autopub = Autopub()

    with pytest.raises(MissingReleaseType):
        autopub.check()


def test_fails_if_release_type_is_not_valid(temporary_working_directory):
    release_file = Path(temporary_working_directory) / "RELEASE.md"
    release_file.write_text("Release type: butter\nThis is not a valid release note")

    autopub = Autopub()

    with pytest.raises(InvalidReleaseType):
        autopub.check()

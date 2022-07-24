from pathlib import Path

import pytest
from autopub import Autopub, AutopubPlugin
from autopub.exceptions import AutopubException, ReleaseFileEmpty, ReleaseFileNotFound, ReleaseNoteInvalid, MissingReleaseType, InvalidReleaseType


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



def test_can_using_plugins_to_add_additional_validation(temporary_working_directory, valid_release_text: str):
    class MissingRocket(AutopubException):
        message = "Missing rocket"

    class MyValidationPlugin(AutopubPlugin):
        def __init__(self):
            self.called = False

        def validate_release_notes(self, release_notes: str):
            if "🚀" not in release_notes:
                raise MissingRocket()

    autopub = Autopub(plugins=[MyValidationPlugin])

    release_file = Path(temporary_working_directory) / "RELEASE.md"
    release_file.write_text(valid_release_text)

    with pytest.raises(MissingRocket):
        autopub.check()


def test_runs_plugin_when_ok(temporary_working_directory, valid_release_text: str):
    release_notes_value = ""

    class MyPlugin(AutopubPlugin):
        def release_notes_valid(self, release_notes: str):
            nonlocal release_notes_value

            release_notes_value = release_notes

    autopub = Autopub(plugins=[MyPlugin])

    release_file = Path(temporary_working_directory) / "RELEASE.md"
    release_file.write_text(valid_release_text)

    autopub.check()

    assert "This is a new release." == release_notes_value

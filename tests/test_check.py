import contextlib
import textwrap
from pathlib import Path
from typing import Any, Generator, Optional

import pytest

from autopub import Autopub, AutopubPlugin
from autopub.exceptions import (
    AutopubException,
    InvalidReleaseType,
    MissingReleaseType,
    ReleaseFileEmpty,
    ReleaseFileNotFound,
    ReleaseNoteInvalid,
)
from autopub.types import ReleaseInfo


@pytest.fixture
def temporary_working_directory(tmpdir: Any) -> Generator[str, None, None]:
    with tmpdir.as_cwd():
        yield tmpdir


def test_check_fails_if_no_release_file_is_present(temporary_working_directory: str):
    autopub = Autopub()

    with pytest.raises(ReleaseFileNotFound):
        autopub.check()


def test_works(temporary_working_directory: str, valid_release_text: str):
    release_file = Path(temporary_working_directory) / "RELEASE.md"
    release_file.write_text(valid_release_text)

    autopub = Autopub()
    release_info = autopub.check()

    assert release_info.release_type == "patch"
    assert release_info.release_notes == "This is a new release."


def test_fails_if_release_note_is_empty(temporary_working_directory: str):
    release_file = Path(temporary_working_directory) / "RELEASE.md"
    release_file.write_text("")

    autopub = Autopub()

    with pytest.raises(ReleaseFileEmpty):
        autopub.check()


def test_fails_if_release_file_is_missing_release_type(temporary_working_directory: str):
    release_file = Path(temporary_working_directory) / "RELEASE.md"
    release_file.write_text("Example \nThis is not a valid release note")

    autopub = Autopub()

    with pytest.raises(MissingReleaseType):
        autopub.check()


def test_fails_if_release_type_is_not_valid(temporary_working_directory: str):
    release_file = Path(temporary_working_directory) / "RELEASE.md"
    release_file.write_text(textwrap.dedent("""
        ---
        release type: butter
        ---
        This is not a valid release note
    """).strip())

    autopub = Autopub()

    with pytest.raises(InvalidReleaseType):
        autopub.check()


def test_can_using_plugins_to_add_additional_validation(
    temporary_working_directory: str, valid_release_text: str
):
    class MissingRocket(AutopubException):
        message = "Missing rocket"

    class MyValidationPlugin(AutopubPlugin):
        def __init__(self):
            self.called = False

        def validate_release_notes(self, release_info: ReleaseInfo):
            if "🚀" not in release_info.release_notes:
                raise MissingRocket()

    autopub = Autopub(plugins=[MyValidationPlugin])

    release_file = Path(temporary_working_directory) / "RELEASE.md"
    release_file.write_text(valid_release_text)

    with pytest.raises(MissingRocket):
        autopub.check()


def test_runs_plugin_when_ok(temporary_working_directory: str, valid_release_text: str):
    release_info_value : Optional[ ReleaseInfo] = None

    class MyPlugin(AutopubPlugin):
        def on_release_notes_valid(self, release_info: ReleaseInfo):
            nonlocal release_info_value

            release_info_value = release_info

    autopub = Autopub(plugins=[MyPlugin])

    release_file = Path(temporary_working_directory) / "RELEASE.md"
    release_file.write_text(valid_release_text)

    autopub.check()

    assert release_info_value
    assert release_info_value.release_notes == "This is a new release."


def test_runs_plugin_when_something_is_wrong(temporary_working_directory: str):
    error_value = ""

    class MyPlugin(AutopubPlugin):
        def on_release_notes_invalid(self, exception: AutopubException):
            nonlocal error_value

            error_value = exception.message

    autopub = Autopub(plugins=[MyPlugin])

    release_file = Path(temporary_working_directory) / "RELEASE.md"
    release_file.write_text("Get a 🚀")

    with contextlib.suppress(MissingReleaseType):
        autopub.check()

    assert "Release note is missing release type" == error_value


def test_supports_old_format(temporary_working_directory: str, deprecated_release_text: str):
    # with pytest.warns(UserWarning):

    release_file = Path(temporary_working_directory) / "RELEASE.md"
    release_file.write_text(deprecated_release_text)

    autopub = Autopub()
    release_info = autopub.check()

    assert release_info.release_type == "patch"
    assert release_info.release_notes == "This is a new release."

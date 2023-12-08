import contextlib
import json
import textwrap
from pathlib import Path

import pytest

from autopub import Autopub, AutopubPlugin
from autopub.exceptions import (
    AutopubException,
    ReleaseFileEmpty,
    ReleaseFileNotFound,
    ReleaseNotesEmpty,
    ReleaseTypeInvalid,
    ReleaseTypeMissing,
)
from autopub.types import ReleaseInfo


def test_check_fails_if_no_release_file_is_present(temporary_working_directory: Path):
    autopub = Autopub()

    with pytest.raises(ReleaseFileNotFound):
        autopub.check()


def test_works(temporary_working_directory: Path, valid_release_text: str):
    release_file = temporary_working_directory / "RELEASE.md"
    release_file.write_text(valid_release_text)

    autopub = Autopub()
    release_info = autopub.check()

    assert release_info.release_type == "patch"
    assert release_info.release_notes == "This is a new release."


def test_fails_if_release_text_is_empty(temporary_working_directory: Path):
    release_file = temporary_working_directory / "RELEASE.md"
    release_file.write_text("")

    autopub = Autopub()

    with pytest.raises(ReleaseFileEmpty):
        autopub.check()


def test_fails_if_release_notes_is_empty(
    temporary_working_directory: Path, missing_release_notes_text: str
):
    release_file = temporary_working_directory / "RELEASE.md"
    release_file.write_text(missing_release_notes_text)

    autopub = Autopub()

    with pytest.raises(ReleaseNotesEmpty):
        autopub.check()


def test_fails_if_release_file_is_missing_release_type(
    temporary_working_directory: Path,
):
    release_file = temporary_working_directory / "RELEASE.md"
    release_file.write_text("Example \nThis is not a valid release note")

    autopub = Autopub()

    with pytest.raises(ReleaseTypeMissing):
        autopub.check()


def test_fails_if_release_type_is_not_valid(temporary_working_directory: Path):
    release_file = temporary_working_directory / "RELEASE.md"
    release_file.write_text(
        textwrap.dedent(
            """
        ---
        release type: butter
        ---
        This is not a valid release note
    """
        ).strip()
    )

    autopub = Autopub()

    with pytest.raises(ReleaseTypeInvalid):
        autopub.check()


def test_can_using_plugins_to_add_additional_validation(
    temporary_working_directory: Path, valid_release_text: str
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

    release_file = temporary_working_directory / "RELEASE.md"
    release_file.write_text(valid_release_text)

    with pytest.raises(MissingRocket):
        autopub.check()


def test_runs_plugin_when_ok(
    temporary_working_directory: Path, valid_release_text: str
):
    release_info_value: ReleaseInfo | None = None

    class MyPlugin(AutopubPlugin):
        def on_release_notes_valid(self, release_info: ReleaseInfo):
            nonlocal release_info_value

            release_info_value = release_info

    autopub = Autopub(plugins=[MyPlugin])

    release_file = temporary_working_directory / "RELEASE.md"
    release_file.write_text(valid_release_text)

    autopub.check()

    assert release_info_value
    assert release_info_value.release_notes == "This is a new release."


def test_runs_plugin_when_something_is_wrong(temporary_working_directory: Path):
    error_value = ""

    class MyPlugin(AutopubPlugin):
        def on_release_notes_invalid(self, exception: AutopubException):
            nonlocal error_value

            error_value = exception.message

    autopub = Autopub(plugins=[MyPlugin])

    release_file = temporary_working_directory / "RELEASE.md"
    release_file.write_text("Get a 🚀")

    with contextlib.suppress(ReleaseTypeMissing):
        autopub.check()

    assert "Release note is missing release type" == error_value


def test_supports_old_format(
    temporary_working_directory: Path, deprecated_release_text: str
):
    release_file = temporary_working_directory / "RELEASE.md"
    release_file.write_text(deprecated_release_text)

    autopub = Autopub()
    release_info = autopub.check()

    assert release_info.release_type == "patch"
    assert release_info.release_notes == "This is a new release."


def test_check_creates_an_artifact(
    temporary_working_directory: Path, valid_release_text: str
):
    working_dir = temporary_working_directory
    release_file = working_dir / "RELEASE.md"
    release_file.write_text(valid_release_text)

    autopub = Autopub()
    autopub.check()

    artifact = working_dir / ".autopub" / "release_info.json"

    assert artifact.exists()

    release_info = json.loads(artifact.read_text())

    assert release_info == {
        "hash": "2081c77abe0980abd6474bdec5d21afceedb7726d6e0c9af3a14d9f24587a268",
        "release_type": "patch",
        "release_notes": "This is a new release.",
        "plugin_data": {},
    }


def test_check_with_plugins_adds_data_to_artifact(temporary_working_directory: Path):
    release_file = temporary_working_directory / "RELEASE.md"
    release_file.write_text(
        textwrap.dedent(
            """
            ---
            release type: patch
            tweet: This is a new release 🙌
            ---
            Valid release notes
            """
        ).strip()
    )

    class TweetPlugin(AutopubPlugin):
        def validate_release_notes(self, release_info: ReleaseInfo):
            self.data["tweet"] = release_info.additional_info["tweet"]

    autopub = Autopub(plugins=[TweetPlugin])
    autopub.check()

    artifact = temporary_working_directory / ".autopub" / "release_info.json"

    assert artifact.exists()

    release_info = json.loads(artifact.read_text())

    assert release_info == {
        "hash": "e866f4cbbf0dbbebee9180395a85dbaeb92eda5890662408fa6a4d47551910e4",
        "release_type": "patch",
        "release_notes": "Valid release notes",
        "plugin_data": {"tweet": "This is a new release 🙌"},
    }

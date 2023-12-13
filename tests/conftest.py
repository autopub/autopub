import json
import shutil
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest

VALID_RELEASE_TEXT = """
---
release type: patch
---

This is a new release.
"""

MISSING_RELEASE_NOTES_TEXT = """
---
release type: patch
---
"""

DEPRECATED_RELEASE_TEXT = """
Release type: patch

This is a new release.
"""


@pytest.fixture
def valid_release_text() -> str:
    return VALID_RELEASE_TEXT.strip()


@pytest.fixture
def missing_release_notes_text() -> str:
    return MISSING_RELEASE_NOTES_TEXT.strip()


@pytest.fixture
def deprecated_release_text() -> str:
    return DEPRECATED_RELEASE_TEXT.strip()


@pytest.fixture(scope="function")
def temporary_working_directory(tmpdir: Any) -> Generator[Path, None, None]:
    with tmpdir.as_cwd():
        yield Path(tmpdir)


@pytest.fixture
def example_project(temporary_working_directory: Path) -> Generator[Path, None, None]:
    project_path = Path(__file__).parent / "fixtures/example-project"

    with temporary_working_directory as dest:
        shutil.copytree(project_path, dest, dirs_exist_ok=True)

        yield dest


@pytest.fixture
def example_project_pdm(
    temporary_working_directory: Path,
) -> Generator[Path, None, None]:
    project_path = Path(__file__).parent / "fixtures/example-project-pdm"

    with temporary_working_directory as dest:
        shutil.copytree(project_path, dest, dirs_exist_ok=True)

        yield dest


@pytest.fixture
def with_valid_artifact(temporary_working_directory: Path) -> Path:
    release_file = temporary_working_directory / "RELEASE.md"
    release_file.write_text("sometext")
    release_info = temporary_working_directory / ".autopub" / "release_info.json"
    release_info.parent.mkdir(parents=True)

    data = {
        "hash": "5fb2054478353fd8d514056d1745b3a9eef066deadda4b90967af7ca65ce6505",
        "release_notes": "foo",
        "release_type": "patch",
        "plugin_data": {},
        "additional_info": {},
        "additional_release_notes": [],
        "version": "1.0.0",
        "previous_version": "0.0.1",
    }
    release_info.write_text(json.dumps(data))

    return release_info

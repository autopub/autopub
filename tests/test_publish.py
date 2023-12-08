import json
from pathlib import Path

import pytest

from autopub import Autopub
from autopub.exceptions import ArtifactHashMismatch, ArtifactNotFound


def test_publish_fails_without_artifact():
    autopub = Autopub()

    with pytest.raises(ArtifactNotFound):
        autopub.publish()


def test_publish_fails_if_hash_is_different(
    temporary_working_directory: Path, valid_release_text: str
):
    release_file = temporary_working_directory / "RELEASE.md"
    release_file.write_text(valid_release_text)

    release_data = {
        "hash": "1234",
        "release_type": "patch",
        "release_notes": "This is a new release.",
    }

    artifact = temporary_working_directory / ".autopub/release_info.json"
    artifact.parent.mkdir(exist_ok=True)
    artifact.write_text(json.dumps(release_data))

    autopub = Autopub()

    with pytest.raises(ArtifactHashMismatch):
        autopub.publish()

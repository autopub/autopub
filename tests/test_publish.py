import pytest

from autopub import Autopub
from autopub.exceptions import ArtifactNotFound


def test_publish_fails_without_artifact():
    autopub = Autopub()

    with pytest.raises(ArtifactNotFound):
        autopub.publish()

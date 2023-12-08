from pathlib import Path

from autopub import Autopub
from autopub.plugins import AutopubPlugin
from autopub.types import ReleaseInfoWithVersion


def test_works(with_valid_artifact: Path):
    prepared = False

    class PreparePlugin(AutopubPlugin):
        def prepare(self, release_info: ReleaseInfoWithVersion) -> None:
            nonlocal prepared
            prepared = True

    autopub = Autopub(plugins=[PreparePlugin])
    autopub.prepare()

    assert prepared


def test_works_post_prepare(with_valid_artifact: Path):
    prepared = False

    class PreparePlugin(AutopubPlugin):
        def post_prepare(self, release_info: ReleaseInfoWithVersion) -> None:
            nonlocal prepared
            prepared = True

    autopub = Autopub(plugins=[PreparePlugin])
    autopub.prepare()

    assert prepared

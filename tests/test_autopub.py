from pathlib import Path

from autopub import Autopub, AutopubPlugin
from autopub.plugins import AutopubBumpVersionPlugin
from autopub.types import ReleaseInfo


class VersionPlugin(AutopubPlugin, AutopubBumpVersionPlugin):
    def post_check(self, release_info: ReleaseInfo):
        self.current_version = "1.0.0"
        self.new_version = "1.0.1"


def test_can_update_info(temporary_working_directory: Path, valid_release_text: str):
    class MyPlugin(AutopubPlugin):
        def post_check(self, release_info: ReleaseInfo):
            release_info.additional_info["tweet"] = "This is a new release 🙌"

        def prepare(self, release_info: ReleaseInfo) -> None:
            release_info.additional_info["prepared"] = True

    autopub = Autopub(plugins=[MyPlugin, VersionPlugin])

    release_file = temporary_working_directory / "RELEASE.md"
    release_file.write_text(valid_release_text)

    autopub.check()

    assert autopub.release_info.additional_info["tweet"] == "This is a new release 🙌"

    autopub.prepare()

    assert autopub.release_info.additional_info["prepared"] is True

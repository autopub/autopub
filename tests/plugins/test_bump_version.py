from pathlib import Path

from autopub.plugins.bump_version import BumpVersionPlugin
from autopub.types import ReleaseInfo


def test_bumps_version_in_pyproject(example_project_pdm: Path):
    info = ReleaseInfo(
        release_type="minor",
        release_notes="",
    )

    assert 'version = "0.1.0"' in (example_project_pdm / "pyproject.toml").read_text()

    plugin = BumpVersionPlugin()
    plugin.prepare(info)

    assert 'version = "0.2.0"' in (example_project_pdm / "pyproject.toml").read_text()


def test_bumps_version_in_pyproject_poetry(example_project: Path):
    info = ReleaseInfo(
        release_type="minor",
        release_notes="",
    )

    assert 'version = "0.1.0"' in (example_project / "pyproject.toml").read_text()

    plugin = BumpVersionPlugin()
    plugin.prepare(info)

    assert 'version = "0.2.0"' in (example_project / "pyproject.toml").read_text()

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
    plugin.post_check(info)
    plugin.post_prepare(info)

    assert 'version = "0.2.0"' in (example_project_pdm / "pyproject.toml").read_text()


def test_bumps_version_in_pyproject_poetry(example_project: Path):
    info = ReleaseInfo(
        release_type="minor",
        release_notes="",
    )

    assert 'version = "0.1.0"' in (example_project / "pyproject.toml").read_text()

    plugin = BumpVersionPlugin()
    plugin.post_check(info)
    plugin.post_prepare(info)

    assert 'version = "0.2.0"' in (example_project / "pyproject.toml").read_text()


def test_bumps_version_in_init_py(example_project_pdm: Path):
    """Test that __version__ in __init__.py is updated."""
    info = ReleaseInfo(
        release_type="patch",
        release_notes="",
    )

    init_file = example_project_pdm / "src" / "__init__.py"
    assert '__version__ = "0.1.0"' in init_file.read_text()

    plugin = BumpVersionPlugin()
    plugin.post_check(info)
    plugin.post_prepare(info)

    assert '__version__ = "0.1.1"' in init_file.read_text()


def test_bumps_version_in_init_py_poetry(example_project: Path):
    """Test that __version__ in __init__.py is updated for poetry projects."""
    info = ReleaseInfo(
        release_type="major",
        release_notes="",
    )

    init_file = example_project / "src" / "__init__.py"
    assert '__version__ = "0.1.0"' in init_file.read_text()

    plugin = BumpVersionPlugin()
    plugin.post_check(info)
    plugin.post_prepare(info)

    assert '__version__ = "1.0.0"' in init_file.read_text()


def test_handles_missing_init_py_gracefully(example_project_pdm: Path):
    """Test that missing __init__.py doesn't cause errors."""
    info = ReleaseInfo(
        release_type="minor",
        release_notes="",
    )

    # Remove the __init__.py file
    init_file = example_project_pdm / "src" / "__init__.py"
    init_file.unlink()

    plugin = BumpVersionPlugin()
    plugin.post_check(info)
    plugin.post_prepare(info)

    # Should still update pyproject.toml
    assert 'version = "0.2.0"' in (example_project_pdm / "pyproject.toml").read_text()


def test_handles_init_without_version_gracefully(example_project_pdm: Path):
    """Test that __init__.py without __version__ doesn't cause errors."""
    info = ReleaseInfo(
        release_type="minor",
        release_notes="",
    )

    # Replace __init__.py content without __version__
    init_file = example_project_pdm / "src" / "__init__.py"
    init_file.write_text("# This is a package\n")

    plugin = BumpVersionPlugin()
    plugin.post_check(info)
    plugin.post_prepare(info)

    # Should still update pyproject.toml
    assert 'version = "0.2.0"' in (example_project_pdm / "pyproject.toml").read_text()
    # __init__.py should remain unchanged
    assert "# This is a package" in init_file.read_text()
    assert "__version__" not in init_file.read_text()

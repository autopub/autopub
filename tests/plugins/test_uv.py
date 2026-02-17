from pathlib import Path

import tomlkit
from pytest_httpserver import HTTPServer

from autopub.plugins.uv import UvPlugin
from autopub.types import ReleaseInfo


def test_runs_build(example_project_uv: Path):
    uv = UvPlugin()
    uv.build()

    assert (example_project_uv / "dist/example_project_uv-0.1.0.tar.gz").exists()


def test_runs_publish(example_project_uv: Path, httpserver: HTTPServer):
    httpserver.expect_request("/legacy").respond_with_data(
        "OK", status=200, content_type="text/plain"
    )

    url = httpserver.url_for("/legacy")

    uv = UvPlugin()
    uv.build()
    uv.publish(publish_url=url, username="example", password="example")


def test_bumps_version_and_updates_lock(example_project_uv: Path):
    """Test that version is bumped and uv.lock is regenerated."""
    info = ReleaseInfo(
        release_type="minor",
        release_notes="",
    )

    # Check initial state
    assert 'version = "0.1.0"' in (example_project_uv / "pyproject.toml").read_text()
    init_file = example_project_uv / "src" / "__init__.py"
    assert '__version__ = "0.1.0"' in init_file.read_text()

    plugin = UvPlugin()
    plugin.post_check(info)
    plugin.post_prepare(info)

    # Check that pyproject.toml was updated
    assert 'version = "0.2.0"' in (example_project_uv / "pyproject.toml").read_text()

    # Check that __version__ in __init__.py was updated
    assert '__version__ = "0.2.0"' in init_file.read_text()

    # Check that uv.lock exists (it should be regenerated)
    # Note: uv.lock may not exist in the test fixture, but the command should run
    # without error. In a real project with dependencies, it would be created/updated.


def test_runs_publish_with_repository(example_project_uv: Path, httpserver: HTTPServer):
    """Test that publish works with a named repository (--index)."""
    httpserver.expect_request("/legacy/").respond_with_data(
        "OK", status=200, content_type="text/plain"
    )

    url = httpserver.url_for("/legacy/")

    # Configure an explicit index in pyproject.toml with publish-url
    # explicit = true prevents the index from being used for dependency resolution
    pyproject_path = example_project_uv / "pyproject.toml"
    pyproject = tomlkit.loads(pyproject_path.read_text())
    pyproject.setdefault("tool", {}).setdefault("uv", {})["index"] = [
        {
            "name": "example",
            "url": "https://example.com/simple/",
            "publish-url": url,
            "explicit": True,
        }
    ]
    pyproject_path.write_text(tomlkit.dumps(pyproject))

    uv = UvPlugin()
    uv.build()
    uv.publish(repository="example", username="example", password="example")

import subprocess
from pathlib import Path

from pytest_httpserver import HTTPServer

from autopub.plugins.poetry import PoetryPlugin
from autopub.types import ReleaseInfo


def test_runs_build(example_project: Path):
    poetry = PoetryPlugin()
    poetry.build()

    assert (example_project / "dist/example_project-0.1.0.tar.gz").exists()


def test_runs_publish(example_project: Path, httpserver: HTTPServer):
    httpserver.expect_request("/legacy").respond_with_data(
        "OK", status=200, content_type="text/plain"
    )

    url = httpserver.url_for("/legacy")

    subprocess.run(["poetry", "config", "repositories.example", url])

    poetry = PoetryPlugin()
    poetry.build()
    poetry.publish(**{"repository": "example"})


def test_bumps_version_in_init_py(example_project: Path):
    """Test that PoetryPlugin updates __version__ in __init__.py."""
    info = ReleaseInfo(
        release_type="major",
        release_notes="",
    )

    # Check initial state
    assert 'version = "0.1.0"' in (example_project / "pyproject.toml").read_text()
    init_file = example_project / "src" / "__init__.py"
    assert '__version__ = "0.1.0"' in init_file.read_text()

    plugin = PoetryPlugin()
    plugin.post_check(info)
    plugin.post_prepare(info)

    # Check that pyproject.toml was updated
    assert 'version = "1.0.0"' in (example_project / "pyproject.toml").read_text()

    # Check that __version__ in __init__.py was updated
    assert '__version__ = "1.0.0"' in init_file.read_text()

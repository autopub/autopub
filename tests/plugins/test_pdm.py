import subprocess
from pathlib import Path

from pytest_httpserver import HTTPServer

from autopub.plugins.pdm import PDMPlugin
from autopub.types import ReleaseInfo


def test_runs_build(example_project_pdm: Path):
    pdm = PDMPlugin()
    pdm.build()

    assert (example_project_pdm / "dist/example_project_pdm-0.1.0.tar.gz").exists()


def test_runs_publish(example_project_pdm: Path, httpserver: HTTPServer):
    httpserver.expect_request("/legacy").respond_with_data(
        "OK", status=200, content_type="text/plain"
    )

    url = httpserver.url_for("/legacy")

    subprocess.run(["pdm", "config", "repository.example.url", url], check=True)
    subprocess.run(
        ["pdm", "config", "repository.example.username", "example"], check=True
    )
    subprocess.run(
        ["pdm", "config", "repository.example.password", "example"], check=True
    )

    try:
        pdm = PDMPlugin()
        pdm.build()
        pdm.publish(
            **{
                "repository": "example",
            }
        )
    finally:
        subprocess.run(
            ["pdm", "config", "--delete", "repository.example.url"], check=True
        )
        subprocess.run(
            ["pdm", "config", "--delete", "repository.example.username"], check=True
        )
        subprocess.run(["pdm", "config", "--delete", "repository.example.password"])


def test_bumps_version_in_init_py(example_project_pdm: Path):
    """Test that PDMPlugin updates __version__ in __init__.py."""
    info = ReleaseInfo(
        release_type="patch",
        release_notes="",
    )

    # Check initial state
    assert 'version = "0.1.0"' in (example_project_pdm / "pyproject.toml").read_text()
    init_file = example_project_pdm / "src" / "__init__.py"
    assert '__version__ = "0.1.0"' in init_file.read_text()

    plugin = PDMPlugin()
    plugin.post_check(info)
    plugin.post_prepare(info)

    # Check that pyproject.toml was updated
    assert 'version = "0.1.1"' in (example_project_pdm / "pyproject.toml").read_text()

    # Check that __version__ in __init__.py was updated
    assert '__version__ = "0.1.1"' in init_file.read_text()

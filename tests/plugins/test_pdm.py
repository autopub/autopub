import subprocess
from pathlib import Path

from pytest_httpserver import HTTPServer

from autopub.plugins.pdm import PDMPlugin


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

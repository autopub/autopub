import subprocess
from pathlib import Path

from pytest_httpserver import HTTPServer

from autopub.plugins.poetry import PoetryPlugin


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

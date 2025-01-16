from pathlib import Path

from pytest_httpserver import HTTPServer

from autopub.plugins.uv import UvPlugin


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

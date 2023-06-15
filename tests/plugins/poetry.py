from pathlib import Path

from autopub.plugins.poetry import PoetryPlugin


def test_runs_build(example_project: Path):
    poetry = PoetryPlugin()
    poetry.build()

    assert (example_project / "dist/example_project-0.1.0.tar.gz").exists()

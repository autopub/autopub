import glob
import os
import sys

sys.path.append(os.path.dirname(__file__))  # noqa

from base import PYPI_URL, run_process


def publish_release():
    env = None
    if PYPI_URL:
        env = {"TWINE_REPOSITORY_URL": PYPI_URL}
    dists = glob.glob("dist/*")
    run_process(
        [sys.executable, "-m", "twine", "upload", "--non-interactive", *dists], env=env
    )

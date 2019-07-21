import os
import sys

sys.path.append(os.path.dirname(__file__))  # noqa

from base import BUILD_SYSTEM, PYPI_URL, run_process

subprocess_output_encoding = "ascii"

if BUILD_SYSTEM == "poetry":
    pub_cmd = ["poetry", "publish", "-u", "$PYPI_USERNAME", "-p", "$PYPI_PASSWORD"]
else:
    pub_cmd = ["twine", "upload", "--repository-url", PYPI_URL, "dist/*"]
    subprocess_output_encoding = "utf-8"


def publish_release():
    run_process(pub_cmd, subprocess_output_encoding)

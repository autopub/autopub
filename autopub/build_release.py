import os
import sys

from base import BUILD_SYSTEM, run_process


sys.path.append(os.path.dirname(__file__))  # noqa


if BUILD_SYSTEM == "poetry":
    build_cmd = ["poetry", "build"]
else:
    build_cmd = ["python", "setup.py", "sdist", "bdist_wheel"]


def build_release():
    run_process(build_cmd)

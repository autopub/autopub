import os
import sys

sys.path.append(os.path.dirname(__file__))  # noqa

from base import git, run_process


def build_release():
    env = None
    if "SOURCE_DATE_EPOCH" not in os.environ:
        ctime = git(["log", "-1", "--pretty=%ct"]).decode().strip()
        env = {"SOURCE_DATE_EPOCH": ctime}
    run_process([sys.executable, "-m", "build"], env=env)

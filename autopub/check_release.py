import os
import sys

sys.path.append(os.path.dirname(__file__))  # noqa

from base import CI_SYSTEM, RELEASE_FILE, run_process


def check_release():
    if not os.path.exists(RELEASE_FILE):
        print("Not releasing a new version because there is no RELEASE file.")
        if CI_SYSTEM == "circleci":
            run_process(["circleci", "step", "halt"])
        elif CI_SYSTEM == "travis":
            sys.exit(1)

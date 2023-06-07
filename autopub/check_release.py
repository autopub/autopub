import os
import sys

sys.path.append(os.path.dirname(__file__))  # noqa

from base import CI_SYSTEM, RELEASE_FILE, run_process


def check_release():
    needs_release = os.path.exists(RELEASE_FILE)
    if not needs_release:
        print("Not releasing a new version because there is no RELEASE file.")
        if CI_SYSTEM == "circleci":
            run_process(["circleci", "step", "halt"])
        elif CI_SYSTEM == "travis":
            sys.exit(1)
    if CI_SYSTEM == "github":
        with open(os.path.expandvars("$GITHUB_OUTPUT"), "a") as f:
            f.write("autopub_release={}\n".format("true" if needs_release else "false"))
